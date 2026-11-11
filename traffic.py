"""One-step traffic forecasts for directed roads."""

import csv
import json
from collections import defaultdict

MULTIPLIERS = {"Low": 1.0, "Medium": 1.15, "High": 1.35}


def forecast(model, observations):
    """Return the next traffic distribution given ordered historical readings."""
    prior = model["initial"]
    for reading in observations:
        if reading not in MULTIPLIERS:
            raise ValueError(f"Unknown traffic observation: {reading}")
        weights = {s: p * model["emission"][s][reading] for s, p in prior.items()}
        total = sum(weights.values())
        if total == 0:
            raise ValueError(f"Impossible traffic observation: {reading}")
        prior = {
            dest: sum(w * model["transition"][s][dest] for s, w in weights.items()) / total
            for dest in prior
        }
    return prior


def adjust_for_traffic(scenario, graph):
    model = json.loads((scenario / "traffic_probabilities.json").read_text())
    histories = defaultdict(list)
    with (scenario / "observed_traffic.csv").open(newline="") as stream:
        for row in csv.DictReader(stream):
            edge = row["from"], row["to"]
            histories[edge].append((int(row["observation_nr"]), row["traffic_observation"]))

    adjusted = {node: [] for node in graph}
    for start, roads in graph.items():
        for end, seconds in roads:
            history = sorted(histories.get((start, end), []))
            probabilities = forecast(model, [reading for _, reading in history])
            factor = sum(p * MULTIPLIERS[s] for s, p in probabilities.items())
            adjusted[start].append((end, seconds * factor))
    return adjusted
