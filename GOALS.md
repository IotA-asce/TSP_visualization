# Project Goals (TSP_visualization)

- [ ] Define the target experience: click points, compute TSP route, visualize it clearly and fast.
- [x] Move `run_game()` behind `if __name__ == "__main__":` to avoid work at import time.
- [x] Add a `requirements.txt` (or `pyproject.toml`) describing `pygame`, `numpy`, `scipy`.
- [ ] Add a simple CLI entrypoint (e.g., `python3 -m tsp_visualization`) with window/solver flags.
- [x] Validate `find_path(points)` inputs and document behavior for `len(points) < 2`.
- [x] Fix naming typos (e.g., `route_distace` -> `route_distance`) and tighten naming consistency.
- [x] Add type hints across the solver and UI boundary (points as `tuple[float, float]`).
- [x] Make `Vector.__mul__` return `NotImplemented` for unsupported operand types.
- [ ] Decide whether `Vector` is core; if yes, migrate to `@dataclass(frozen=True)`.

- [x] Factor distance computation into a pure helper and unit test it.
- [ ] Keep the brute-force solver as a reference implementation for small `n`.
- [ ] Add a nearest-neighbor heuristic solver for interactive responsiveness.
- [ ] Add 2-opt improvement on top of an initial tour.
- [ ] Add a “solver strategy” selector (brute-force vs heuristic) based on `n`.
- [ ] Add an optional time budget / iteration cap for heuristics.
- [ ] Keep solver deterministic by default; add seeding if randomness is introduced.
- [ ] Avoid recomputing the full route on every frame; only recompute on input changes.
- [ ] (Optional) Offload heavy solver runs to a background thread/process to keep UI smooth.
- [x] Display route length (and maybe compute time) on-screen.

- [x] Add keyboard shortcuts: undo last point, clear points, recompute.
- [ ] Add a “closed tour” toggle (return to start vs open path).
- [ ] Improve drawing: anti-aliased lines, thicker path, distinct start/end markers.
- [ ] Add animated path drawing (progressively reveal the tour).
- [ ] Add drag-to-move points and update the route on release.
- [ ] Add pan/zoom to support large coordinate ranges.
- [ ] Handle window resizing cleanly (re-center UI, maintain aspect).
- [ ] Add a "save points" and "load points" feature (JSON or CSV).

- [ ] Add "export image" (PNG) of the current scene.
- [ ] Add reproducible demo datasets (small, medium) for quick manual testing.
- [ ] Add a non-interactive benchmark script to compare solver strategies.
- [x] Add unit tests for `path_search.py` on tiny inputs (2-8 points).
- [x] Add unit tests for `vector.py` operations and edge cases (zero normalization, div by zero).
- [x] Add a smoke test that imports modules without side effects.
- [x] Add `ruff` configuration and wire up `ruff check` + `ruff format`.
- [x] Add `mypy` configuration and basic typing discipline for new code.
- [ ] Add GitHub Actions CI for lint + typecheck + tests.

- [ ] Expand `README.md` (keep UTF-16 encoding intact) with setup, usage, and limitations.
- [ ] Document algorithmic complexity and recommended point limits in the UI.
- [ ] Add lightweight developer notes on architecture boundaries (UI vs solver vs math).
- [ ] Add structured error messages and graceful exits (quit, missing deps, invalid inputs).
