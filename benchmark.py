"""Simple benchmark harness for TSP solvers.

Examples:
  python3 benchmark.py --n 50 --strategy nearest_two_opt
  python3 benchmark.py --n 9 --strategy bruteforce
"""

from __future__ import annotations

import argparse
import math
import random
import time

from path_search import find_path


def path_length(path: list[tuple[float, float]], *, closed: bool) -> float:
    if len(path) < 2:
        return 0.0

    total = 0.0
    for i in range(len(path) - 1):
        x1, y1 = path[i]
        x2, y2 = path[i + 1]
        total += math.hypot(x2 - x1, y2 - y1)

    if closed:
        x1, y1 = path[-1]
        x2, y2 = path[0]
        total += math.hypot(x2 - x1, y2 - y1)

    return total


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=30, help="Number of points")
    parser.add_argument("--seed", type=int, default=0, help="Random seed")
    parser.add_argument(
        "--strategy",
        type=str,
        default="auto",
        help="auto|bruteforce|nearest|two_opt|nearest_two_opt",
    )
    parser.add_argument("--open", action="store_true", help="Treat route as an open path")
    parser.add_argument("--repeats", type=int, default=3, help="Repeat runs and report best")
    args = parser.parse_args()

    if args.n < 0:
        raise SystemExit("--n must be >= 0")
    if args.repeats < 1:
        raise SystemExit("--repeats must be >= 1")

    rng = random.Random(args.seed)
    points = [(rng.uniform(0, 1000), rng.uniform(0, 1000)) for _ in range(args.n)]
    closed = not args.open

    best_s = float("inf")
    best_len = float("inf")

    for _ in range(args.repeats):
        t0 = time.perf_counter()
        path = find_path(points, strategy=args.strategy, closed=closed)
        dt = time.perf_counter() - t0
        length = path_length(path, closed=closed)

        best_s = min(best_s, dt)
        best_len = min(best_len, length)

    print(f"n={args.n} closed={closed} strategy={args.strategy}")
    print(f"best_time_s={best_s:.6f} best_length={best_len:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
