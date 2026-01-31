"""CLI entrypoint for running the TSP visualizer.

Examples:
  python3 -m tsp_visualization
  python3 -m tsp_visualization --load data/small.json
  python3 -m tsp_visualization --strategy nearest_two_opt --open
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _load_points(path: Path) -> list[tuple[float, float]]:
    data = json.loads(path.read_text(encoding="utf-8"))

    if isinstance(data, dict) and "points" in data:
        data = data["points"]

    if not isinstance(data, list):
        raise ValueError("expected a list of [x, y] points or an object with a 'points' key")

    out: list[tuple[float, float]] = []
    for p in data:
        if not isinstance(p, list) or len(p) != 2:
            raise ValueError("each point must be [x, y]")
        out.append((float(p[0]), float(p[1])))
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tsp_visualization")
    parser.add_argument(
        "--load",
        type=Path,
        default=None,
        help="Load points from JSON (e.g. points.json or data/small.json)",
    )
    parser.add_argument(
        "--strategy",
        type=str,
        default="auto",
        help="auto|bruteforce|nearest|two_opt|nearest_two_opt",
    )

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--closed", action="store_true", help="Use a closed tour")
    mode.add_argument("--open", action="store_true", help="Use an open path")

    args = parser.parse_args(argv)

    closed = True
    if args.open:
        closed = False
    elif args.closed:
        closed = True

    initial_points: list[tuple[float, float]] | None = None
    if args.load is not None:
        initial_points = _load_points(args.load)

    from game_screen import run_game

    run_game(initial_points=initial_points, closed=closed, strategy=args.strategy)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
