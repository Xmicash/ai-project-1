import argparse
from pathlib import Path

from road_conditions import estimate_graph
from traffic import adjust_for_traffic
from routing import fastest_route, load_graph


def main():
    parser = argparse.ArgumentParser(description="Inspect estimated travel times")
    parser.add_argument("scenario", type=Path)
    parser.add_argument("--route", nargs=2, metavar=("FROM", "TO"))
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--roads-only", action="store_true", help="omit the traffic forecast")
    mode.add_argument("--baseline", action="store_true", help="assume every road is open")
    args = parser.parse_args()
    try:
        graph = load_graph(args.scenario)
        if not args.baseline:
            graph = estimate_graph(args.scenario, graph)
            if not args.roads_only:
                graph = adjust_for_traffic(args.scenario, graph)
        if args.route:
            result = fastest_route(graph, *args.route)
            if result is None:
                print("No directed route connects these nodes.")
            else:
                path, seconds = result
                print(f"{' -> '.join(path)} ({seconds:.2f} s)")
        else:
            print(f"{len(graph)} nodes, {sum(map(len, graph.values()))} directed roads")
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
