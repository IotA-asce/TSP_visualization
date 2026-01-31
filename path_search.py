"""TSP route search.

`find_path(points)` returns an ordering of the provided points that minimizes total tour
length, treating the tour as a *closed loop* (last point connects back to the first).

Implementation note: this is a brute-force solver (O(n!)). Keep point counts small.
"""

from __future__ import annotations

from collections.abc import Sequence
from itertools import permutations
from typing import TypeAlias

try:
    import numpy as np
except ModuleNotFoundError as exc:  # pragma: no cover
    raise ModuleNotFoundError(
        "numpy is required for path_search; install dependencies via 'pip install -r requirements.txt'"
    ) from exc

if not hasattr(np, "asarray"):  # pragma: no cover
    raise ModuleNotFoundError(
        "numpy is required for path_search; install dependencies via 'pip install -r requirements.txt'"
    )

Point: TypeAlias = tuple[float, float]


def _route_distance(distances: np.ndarray, route: Sequence[int]) -> float:
    """Compute closed-tour distance for an index route."""
    if not route:
        return 0.0

    total = 0.0
    route_len = len(route)
    for i in range(route_len):
        total += float(distances[route[i], route[(i + 1) % route_len]])
    return total


def find_path(points: Sequence[Point]) -> list[Point]:
    """Return the shortest closed tour through `points`.

    For `len(points) < 2`, this returns a list copy of `points`.
    """
    points_list = list(points)
    n = len(points_list)
    if n < 2:
        return points_list

    points_array = np.asarray(points_list, dtype=float)
    if points_array.shape != (n, 2):
        raise ValueError("points must be a sequence of (x, y) pairs")

    from scipy.spatial.distance import cdist

    distances = cdist(points_array, points_array)

    all_routes = permutations(range(n))
    shortest_route = min(
        all_routes, key=lambda route: _route_distance(distances, route)
    )
    return [points_list[i] for i in shortest_route]
