import argparse
from pathlib import Path

from routing import fastest_route, load_graph


def main():
    parser = argparse.ArgumentParser(description="Inspect travel times on open roads")
    parser.add_argument("scenario", type=Path)
    parser.add_argument("--route", nargs=2, metavar=("FROM", "TO"))
    args = parser.parse_args()
    try:
        graph = load_graph(args.scenario)
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
