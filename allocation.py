"""Online dispatch with backtracking over simultaneous assignments."""

import csv
import json
from dataclasses import dataclass
from routing import fastest_route

PRIORITIES = ("Critical", "High", "Medium", "Low")


@dataclass
class Responder:
    id: str
    location: str
    skills: set
    ready: float


@dataclass(frozen=True)
class Incident:
    id: str
    location: str
    priority: str
    deadline: float
    skill: str
    release: float
    duration: float


def read_inputs(folder):
    with (folder / "responders.csv").open(newline="") as stream:
        responders = [Responder(r["responder_id"], r["start_location"],
                                set(r["capabilities"].split(";")),
                                float(r["time_until_available"]) if r["availability"] == "Busy" else 0)
                      for r in csv.DictReader(stream)]
    with (folder / "incidents.csv").open(newline="") as stream:
        incidents = [Incident(i["incident_id"], i["location"], i["priority"],
                              float(i["deadline"]), i["required_capability"],
                              float(i["timestamp"]), float(i["time_required"]))
                     for i in csv.DictReader(stream)]
    return responders, incidents


def choose_batch(graph, now, pending, responders):
    domains = []
    for incident in pending:
        choices = []
        for r in responders:
            if r.ready <= now and incident.skill in r.skills:
                route = fastest_route(graph, r.location, incident.location)
                if route and now + route[1] <= incident.deadline:
                    choices.append((r, route))
        if choices:
            domains.append((incident, choices))

    best_score = None
    best = []

    def search(index, used, batch, counts, response_time):
        nonlocal best_score, best
        if index == len(domains):
            score = (*counts, -response_time)
            if best_score is None or score > best_score:
                best_score, best = score, batch.copy()
            return
        incident, choices = domains[index]
        priority = PRIORITIES.index(incident.priority)
        for responder, (path, travel) in choices:
            if responder.id in used:
                continue
            used.add(responder.id)
            counts[priority] += 1
            batch.append((incident, responder, path, travel))
            search(index + 1, used, batch, counts, response_time + now - incident.release + travel)
            batch.pop()
            counts[priority] -= 1
            used.remove(responder.id)
        search(index + 1, used, batch, counts, response_time)

    search(0, set(), [], [0] * len(PRIORITIES), 0)
    return best


def simulate(graph, responders, incidents):
    pending = list(incidents)
    now = 0
    plan = []
    delays = []
    while pending:
        visible = [i for i in pending if i.release <= now <= i.deadline]
        batch = choose_batch(graph, now, visible, responders)
        for incident, r, path, travel in batch:
            plan.append(dict(responder_id=r.id, incident_id=incident.id, path=path, time=now))
            r.location = incident.location
            r.ready = now + travel + incident.duration
            delays.append(now + travel - incident.release)
            pending.remove(incident)
        if any(r.ready <= now for _, r, _, _ in batch):
            continue  # A zero-duration assignment can release a responder immediately.
        events = [i.release for i in pending if i.release > now]
        events.extend(r.ready for r in responders if r.ready > now)
        if not events:
            break
        now = min(events)
    return plan, delays


def write_outputs(folder, plan, delays, total):
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "plan.json").write_text(json.dumps(plan, indent=2) + "\n")
    mean = f"{sum(delays) / len(delays):.2f} s" if delays else "N/A"
    percentage = f"{100 * len(plan) / total:.2f}%" if total else "N/A"
    summary = (f"Incidents handled: {len(plan)}/{total}\n"
               f"Responders used: {len({a['responder_id'] for a in plan})}\n"
               f"Average response time: {mean}\nDeadlines met: {percentage}\n")
    (folder / "statistics.txt").write_text(summary)
    return summary
