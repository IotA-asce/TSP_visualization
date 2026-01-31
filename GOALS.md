# Project Goals (TSP_visualization)

- [x] Define the target experience: click points, compute TSP route, visualize it clearly and fast.
- [x] Move `run_game()` behind `if __name__ == "__main__":` to avoid work at import time.
- [x] Add a `requirements.txt` (or `pyproject.toml`) describing `pygame`, `numpy`, `scipy`.
- [x] Add a simple CLI entrypoint (e.g., `python3 -m tsp_visualization`) with window/solver flags.
- [x] Validate `find_path(points)` inputs and document behavior for `len(points) < 2`.
- [x] Fix naming typos (e.g., `route_distace` -> `route_distance`) and tighten naming consistency.
- [x] Add type hints across the solver and UI boundary (points as `tuple[float, float]`).
- [x] Make `Vector.__mul__` return `NotImplemented` for unsupported operand types.
- [x] Decide whether `Vector` is core; if yes, migrate to `@dataclass(frozen=True)`.

- [x] Factor distance computation into a pure helper and unit test it.
- [x] Keep the brute-force solver as a reference implementation for small `n`.
- [x] Add a nearest-neighbor heuristic solver for interactive responsiveness.
- [x] Add 2-opt improvement on top of an initial tour.
- [x] Add a “solver strategy” selector (brute-force vs heuristic) based on `n`.
- [x] Add an optional time budget / iteration cap for heuristics.
- [x] Keep solver deterministic by default; add seeding if randomness is introduced.
- [x] Avoid recomputing the full route on every frame; only recompute on input changes.
- [x] (Optional) Offload heavy solver runs to a background thread/process to keep UI smooth.
- [x] Display route length (and maybe compute time) on-screen.

- [x] Add keyboard shortcuts: undo last point, clear points, recompute.
- [x] Add a “closed tour” toggle (return to start vs open path).
- [x] Improve drawing: anti-aliased lines, thicker path, distinct start/end markers.
- [x] Add animated path drawing (progressively reveal the tour).
- [x] Add drag-to-move points and update the route on release.
- [x] Add pan/zoom to support large coordinate ranges.
- [x] Handle window resizing cleanly (re-center UI, maintain aspect).
- [x] Add a "save points" and "load points" feature (JSON or CSV).

- [x] Add "export image" (PNG) of the current scene.
- [x] Add reproducible demo datasets (small, medium) for quick manual testing.
- [x] Add a non-interactive benchmark script to compare solver strategies.
- [x] Add unit tests for `path_search.py` on tiny inputs (2-8 points).
- [x] Add unit tests for `vector.py` operations and edge cases (zero normalization, div by zero).
- [x] Add a smoke test that imports modules without side effects.
- [x] Add `ruff` configuration and wire up `ruff check` + `ruff format`.
- [x] Add `mypy` configuration and basic typing discipline for new code.
- [x] Add GitHub Actions CI for lint + typecheck + tests.

- [x] Expand `README.md` (keep UTF-16 encoding intact) with setup, usage, and limitations.
- [x] Document algorithmic complexity and recommended point limits in the UI.
- [x] Add lightweight developer notes on architecture boundaries (UI vs solver vs math).
- [x] Add structured error messages and graceful exits (quit, missing deps, invalid inputs).

# Phase 2: Interactivity & Games

## Mini-Games
- [x] **"Human vs Solver" Mode**:
    - [x] Add a "Drawing Mode" where the user clicks points sequentially to define their own path.
    - [x] Compare User Path Length vs Solver Path Length (Score = `Solver / User * 100`).
    - [x] Display a "Scoreboard" or comparison overlay.
- [ ] **"Untangle" (Manual 2-Opt) Game**:
    - [ ] Generate a random "tangled" path (lots of crossings).
    - [ ] Allow users to click two edges to perform a swap (manual 2-opt).
    - [ ] Goal: Untangle the path to match (or beat) a target length.

## Enhanced Visualization
- [ ] **Step-by-Step Algorithm View**:
    - [ ] Refactor `path_search.py` solvers to be Python generators (`yield` intermediate states).
    - [ ] Visualize the "search" process (e.g., Nearest Neighbor "looking" for the next point).
    - [ ] Visualize 2-opt swaps happening in slow motion (flash edges red/green).
- [ ] **Minimum Spanning Tree (MST) Overlay**:
    - [ ] Implement Prim's or Kruskal's algorithm.
    - [ ] Toggle to draw the MST in the background (faint lines) to show the point "skeleton".
- [ ] **Alternative Metrics**:
    - [ ] Add support for Manhattan Distance (`|x1-x2| + |y1-y2|`).
    - [ ] Add a UI toggle to switch between Euclidean and Manhattan metrics.
