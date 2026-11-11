"""Uniform-cost search on directed roads, with travel times in seconds."""

import heapq
import json


def load_graph(scenario):
    data = json.loads((scenario / "city_graph.json").read_text(encoding="utf-8"))
    graph = {node["id"]: [] for node in data["nodes"]}
    for road in data["roads"]:
        start, end = road["from"], road["to"]
        if start not in graph or end not in graph:
            raise ValueError(f"Unknown road endpoint: {start} -> {end}")
        if road["speed"] <= 0 or road["distance"] < 0:
            raise ValueError(f"Invalid speed or distance: {start} -> {end}")
        graph[start].append((end, road["distance"] / road["speed"]))
    return graph


def fastest_route(graph, start, goal):
    """Return (path, seconds), or None if the destination is unreachable."""
    if start not in graph or goal not in graph:
        raise ValueError("Both endpoints must be nodes in the scenario")
    frontier = [(0.0, start)]
    best = {start: 0.0}
    parent = {}
    while frontier:
        elapsed, node = heapq.heappop(frontier)
        if elapsed > best[node]:
            continue
        if node == goal:
            path = [goal]
            while path[-1] != start:
                path.append(parent[path[-1]])
            return path[::-1], elapsed
        for neighbor, seconds in graph[node]:
            arrival = elapsed + seconds
            if arrival < best.get(neighbor, float("inf")):
                best[neighbor] = arrival
                parent[neighbor] = node
                heapq.heappush(frontier, (arrival, neighbor))
    return None
