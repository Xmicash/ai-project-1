"""Bayesian road-status estimates for directed roads."""

import csv
import json
from collections import defaultdict

STATES = ("Blocked", "Congested", "Open")  # Prefer the safer decision on a tie.


def posterior(tables, reports):
    weather = {row["weather"] for row in reports if row["weather"]}
    priors = tables["road_status_given_weather"]
    if len(weather) > 1:
        raise ValueError("Conflicting weather observations for the same directed road")
    if weather:
        weights = priors[weather.pop()].copy()
    else:
        weights = {
            state: sum(p * priors[w][state] for w, p in tables["weather_prior"].items())
            for state in STATES
        }
    for row in reports:
        likelihood = tables[row["source"].lower() + "_report"]
        for state in STATES:
            weights[state] *= likelihood[state][row["reported_status"]]
    total = sum(weights.values())
    if total == 0:
        raise ValueError("Reports have zero probability under the supplied model")
    return {state: weight / total for state, weight in weights.items()}


def estimate_graph(scenario, graph):
    tables = json.loads((scenario / "road_probabilities.json").read_text())
    reports = defaultdict(list)
    with (scenario / "road_reports.csv").open(newline="") as file:
        for row in csv.DictReader(file):
            reports[row["from"], row["to"]].append(row)

    adjusted = {node: [] for node in graph}
    for start, roads in graph.items():
        for end, seconds in roads:
            probabilities = posterior(tables, reports.get((start, end), []))
            status = max(STATES, key=probabilities.get)
            if status != "Blocked":
                multiplier = 1.5 if status == "Congested" else 1.0
                adjusted[start].append((end, seconds * multiplier))
    return adjusted
