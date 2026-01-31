"""TSP route search.

This module powers the interactive Pygame visualization.

Core API:
- `find_path(points, strategy="auto", closed=True, time_budget_s=None)`

The default strategy is intentionally pragmatic:
- For small point counts, use brute force (optimal but factorial-time).
- For larger point counts, use heuristics (nearest-neighbor + 2-opt) to stay responsive.
"""

from __future__ import annotations

import math
import time
from collections.abc import Iterable, Sequence
from itertools import permutations
from typing import Literal, TypeAlias

Point: TypeAlias = tuple[float, float]
Strategy: TypeAlias = Literal[
    "auto",
    "bruteforce",
    "nearest",
    "two_opt",
    "nearest_two_opt",
]


def _coerce_points(points: Iterable[object]) -> list[Point]:
    out: list[Point] = []
    for p in points:
        if not isinstance(p, Sequence) or len(p) != 2:
            raise ValueError("points must be a sequence of (x, y) pairs")
        x, y = p
        out.append((float(x), float(y)))
    return out


def _distance_matrix(points: Sequence[Point]) -> list[list[float]]:
    """Build a symmetric distance matrix.

    Uses SciPy/Numpy if available, otherwise falls back to pure Python.
    """
    n = len(points)

    try:  # fast path
        import numpy as np  # type: ignore

        if hasattr(np, "asarray"):
            from scipy.spatial.distance import cdist  # type: ignore

            arr = np.asarray(points, dtype=float)  # type: ignore[attr-defined]
            d = cdist(arr, arr)
            return [[float(d[i, j]) for j in range(n)] for i in range(n)]
    except ModuleNotFoundError:
        pass

    dists: list[list[float]] = [[0.0] * n for _ in range(n)]
    for i in range(n):
        x1, y1 = points[i]
        for j in range(i + 1, n):
            x2, y2 = points[j]
            dist = math.hypot(x2 - x1, y2 - y1)
            dists[i][j] = dist
            dists[j][i] = dist
    return dists


def _route_length(
    distances: Sequence[Sequence[float]],
    route: Sequence[int],
    *,
    closed: bool,
) -> float:
    if len(route) < 2:
        return 0.0

    total = 0.0
    for i in range(len(route) - 1):
        total += float(distances[route[i]][route[i + 1]])
    if closed:
        total += float(distances[route[-1]][route[0]])
    return total


def _solve_bruteforce(
    distances: Sequence[Sequence[float]],
    *,
    closed: bool,
) -> list[int]:
    n = len(distances)
    if n < 2:
        return list(range(n))

    if closed:
        # A closed cycle is rotation-invariant; fix node 0 as the start to reduce work.
        rest = range(1, n)
        best_route: tuple[int, ...] | None = None
        best_len = float("inf")
        for perm in permutations(rest):
            route = (0, *perm)
            length = _route_length(distances, route, closed=True)
            if length < best_len:
                best_len = length
                best_route = route
        return list(best_route) if best_route is not None else list(range(n))

    best_route = min(
        permutations(range(n)),
        key=lambda route: _route_length(distances, route, closed=False),
    )
    return list(best_route)


def _solve_nearest_neighbor(
    distances: Sequence[Sequence[float]],
    *,
    closed: bool,
    time_budget_s: float | None,
) -> list[int]:
    n = len(distances)
    if n < 2:
        return list(range(n))

    start_time = time.perf_counter()

    best_route: list[int] | None = None
    best_len = float("inf")

    for start in range(n):
        if time_budget_s is not None and (time.perf_counter() - start_time) > time_budget_s:
            break

        unvisited = set(range(n))
        unvisited.remove(start)
        route = [start]
        current = start
        while unvisited:
            nxt = min(unvisited, key=lambda j: distances[current][j])
            unvisited.remove(nxt)
            route.append(nxt)
            current = nxt

        length = _route_length(distances, route, closed=closed)
        if length < best_len:
            best_len = length
            best_route = route

    return best_route if best_route is not None else list(range(n))


def _two_opt(
    route: list[int],
    distances: Sequence[Sequence[float]],
    *,
    closed: bool,
    time_budget_s: float | None,
) -> list[int]:
    n = len(route)
    if n < 4:
        return route

    start_time = time.perf_counter()
    improved = True

    while improved:
        improved = False
        # For a closed loop, keep route[0] fixed to avoid equivalent rotations.
        i_start = 1 if closed else 0
        i_end = n - 2

        for i in range(i_start, i_end + 1):
            if time_budget_s is not None and (time.perf_counter() - start_time) > time_budget_s:
                return route

            k_start = i + 1
            k_end = n - 1 if closed else n - 2
            for k in range(k_start, k_end + 1):
                if time_budget_s is not None and (time.perf_counter() - start_time) > time_budget_s:
                    return route

                a = route[i - 1] if i > 0 else None
                b = route[i]
                c = route[k]
                d = route[(k + 1) % n] if closed else route[k + 1]

                if a is None:
                    continue

                before = distances[a][b] + distances[c][d]
                after = distances[a][c] + distances[b][d]
                if after + 1e-12 < before:
                    route[i : k + 1] = reversed(route[i : k + 1])
                    improved = True

        if not improved:
            break

    return route


def find_path(
    points: Sequence[Point],
    *,
    strategy: Strategy = "auto",
    closed: bool = True,
    time_budget_s: float | None = None,
) -> list[Point]:
    """Return an ordering of `points` representing a good (or optimal) tour.

    Args:
        points: Sequence of (x, y) coordinates.
        strategy:
            - "auto": brute force for small n; otherwise nearest-neighbor + 2-opt.
            - "bruteforce": exact solver (factorial-time).
            - "nearest": nearest-neighbor heuristic.
            - "two_opt": 2-opt improvement starting from the input order.
            - "nearest_two_opt": nearest-neighbor then 2-opt.
        closed: If True, treat the tour as a cycle (last connects to first).
        time_budget_s: Optional time budget for heuristic improvements.

    Returns:
        A list containing the same points, re-ordered.
    """
    points_list = _coerce_points(points)
    n = len(points_list)
    if n < 2:
        return list(points_list)

    if strategy == "auto":
        strategy = "bruteforce" if n <= 10 else "nearest_two_opt"

    distances = _distance_matrix(points_list)

    if strategy == "bruteforce":
        route = _solve_bruteforce(distances, closed=closed)
        return [points_list[i] for i in route]

    if strategy == "nearest":
        route = _solve_nearest_neighbor(
            distances,
            closed=closed,
            time_budget_s=time_budget_s,
        )
        return [points_list[i] for i in route]

    if strategy == "two_opt":
        route = list(range(n))
        route = _two_opt(route, distances, closed=closed, time_budget_s=time_budget_s)
        return [points_list[i] for i in route]

    if strategy == "nearest_two_opt":
        route = _solve_nearest_neighbor(
            distances,
            closed=closed,
            time_budget_s=time_budget_s,
        )
        route = _two_opt(route, distances, closed=closed, time_budget_s=time_budget_s)
        return [points_list[i] for i in route]

    raise ValueError(f"Unknown strategy: {strategy!r}")
