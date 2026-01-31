# Agent Notes (TSP_visualization)

This repository is a small Python project that visualizes a Traveling Salesman Problem (TSP)
path in a Pygame window.

Cursor rules / Copilot rules:
- No `.cursor/rules/`, `.cursorrules`, or `.github/copilot-instructions.md` found in this repo.

Repo layout:
- `game_screen.py`: Pygame loop; collects mouse-click points and draws the computed path.
- `path_search.py`: `find_path(points)` computes a path (currently brute-force via permutations).
- `vector.py`: lightweight `Vector` helper class (math ops + utilities).

----------------------------------------
Commands

Runtime / "build":
- Run the interactive app:
  - `python3 game_screen.py`

Non-interactive smoke checks:
- Quick solver sanity check (no Pygame):
  - `python3 -c "from path_search import find_path; print(find_path([(0,0),(1,0),(0,1)]))"`

Dependencies:
- The code imports `pygame`, `numpy`, and `scipy`.
- Typical setup (venv recommended):
  - `python3 -m venv .venv`
  - `source .venv/bin/activate`
  - `python3 -m pip install -U pip`
  - `python3 -m pip install pygame numpy scipy`

Lint + format (recommended; not currently configured in-repo):
- Install tools:
  - `python3 -m pip install -U ruff`
- Lint:
  - `python3 -m ruff check .`
- Format:
  - `python3 -m ruff format .`

Type-check (recommended; not currently configured in-repo):
- Install tools:
  - `python3 -m pip install -U mypy`
- Run:
  - `python3 -m mypy .`

Tests (none currently checked in):
- If/when `pytest` tests exist:
  - Install: `python3 -m pip install -U pytest`
  - Run all: `python3 -m pytest`
  - Run a single file: `python3 -m pytest tests/test_path_search.py`
  - Run a single test by node id:
    - `python3 -m pytest tests/test_path_search.py::test_two_points`
  - Run tests matching a substring:
    - `python3 -m pytest -k path -q`
  - Stop on first failure:
    - `python3 -m pytest -x`

- If using the stdlib `unittest` instead:
  - Run all: `python3 -m unittest`
  - Run a single test module: `python3 -m unittest tests.test_path_search`
  - Run a single test case/method:
    - `python3 -m unittest tests.test_path_search.TestTsp.test_two_points`

Quick manual sanity checks:
- Start the app and click a few points; the path should update without exceptions.
- Keep point counts small; the current algorithm is factorial-time.

----------------------------------------
Code Style Guidelines

General:
- Prefer small, pure functions with explicit inputs/outputs.
- Keep interactive/UI code (`pygame` loop) separate from algorithmic code.
- Avoid work at import time in library modules; use `if __name__ == "__main__":` for entrypoints.

Formatting:
- Follow PEP 8.
- Keep lines readable; when in doubt, wrap at ~88-100 chars.
- Use trailing commas in multi-line literals/calls.

Imports:
- Order: standard library, third-party, local imports.
- One import per line when it improves diffs/readability.
- Avoid wildcard imports.
- Local imports should be explicit (e.g., `from path_search import find_path`).

Types:
- Add type hints for new/modified functions.
- Prefer concrete, simple types:
  - Points are currently `(int, int)` or `(float, float)` tuples.
  - Use `Sequence[tuple[float, float]]` / `list[tuple[int, int]]` as appropriate.
- If `Vector` becomes a core type, consider migrating to `@dataclass(frozen=True)` and adding
  numeric protocols where helpful.

Naming:
- Functions/variables: `snake_case`.
- Classes: `PascalCase`.
- Constants: `UPPER_SNAKE_CASE`.
- Use descriptive names (e.g., `route_distance`, not `route_distace`).

Error handling:
- Raise specific exceptions with actionable messages.
- Validate inputs at module boundaries:
  - `find_path(points)` should define behavior for `len(points) < 2`.
- In the Pygame loop, handle quit events cleanly (`pygame.quit()` then exit).
- Avoid catching broad exceptions unless re-raising with context.

Algorithmic performance:
- Be explicit about complexity; the current brute-force TSP solver is O(n!).
- If adding heuristics (nearest neighbor, 2-opt, simulated annealing, etc.):
  - Keep the solver deterministic by default (seed randomness if used).
  - Separate "compute" from "render" so UI stays responsive.
  - Consider incremental updates rather than recomputing from scratch per click.

Numerics (NumPy/SciPy):
- Prefer vectorized operations when they simplify the code.
- Avoid unnecessary conversions between lists/tuples and arrays.
- Keep coordinate dtype consistent (ints for screen coords; floats for math).

Pygame specifics:
- Keep a stable framerate (`clock.tick(60)` is fine).
- Avoid heavy computation inside the event loop; if needed, compute on click or offload.
- Use explicit RGB tuples (or named colors) consistently.

Vector conventions (`vector.py`):
- `__mul__` currently supports scalar and elementwise vector multiply; document or split if ambiguous.
- Prefer returning `NotImplemented` for unsupported operand types rather than silently returning None.
- Equality on floats should use tolerances (`math.isclose`) when floats are introduced.

Documentation:
- Add docstrings to any non-trivial function (especially solver functions).
- Keep module-level comments factual; avoid stale TODOs.

Repo hygiene:
- Note: `README.md` is UTF-16 LE with CRLF; only change encoding intentionally.
- Avoid committing runtime artifacts (`__pycache__/`, `.venv/`).

Testing guidelines (when adding tests):
- Prefer deterministic unit tests for `path_search.py` and `vector.py`.
- Avoid opening Pygame windows in CI/unit tests; keep rendering as manual/smoke testing.
- Keep test inputs small (brute-force TSP is factorial-time).

----------------------------------------
Working Agreement For Agents

- Do not introduce new tooling (ruff/pytest/mypy) unless the change request benefits from it.
- If you add a new dependency, document it and keep the install steps simple.
- Prefer minimal diffs; keep behavior the same unless the task requests a change.
