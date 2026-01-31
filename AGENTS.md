# Agent Notes (TSP_visualization)

This repository is a small Python project that visualizes a Traveling Salesman Problem (TSP)
path in a Pygame window.

Cursor rules / Copilot rules:
- No `.cursor/rules/`, `.cursorrules`, or `.github/copilot-instructions.md` found in this repo.

Repo layout:
- `game_screen.py`: Main Pygame UI; collects points, draws route, handles threading/save/load.
- `path_search.py`: `find_path(points, ...)` solver with strategies (brute-force, nearest, 2-opt).
- `vector.py`: lightweight `Vector` helper class (math ops + utilities); optional/utility only.
- `tsp_visualization.py`: CLI entrypoint wrapper around `game_screen.py`.
- `benchmark.py`: Non-interactive script to benchmark solver strategies.
- `data/`: Demo datasets (JSON).
- `tests/`: Unittest suite.

----------------------------------------
Commands

Runtime / "build":
- Run the interactive app:
  - `python3 game_screen.py`
  - OR `python3 -m tsp_visualization`

Non-interactive smoke checks:
- Quick solver sanity check (no Pygame):
  - `python3 -c "from path_search import find_path; print(find_path([(0,0),(1,0),(0,1)]))"`

Dependencies:
- The code imports `pygame` (UI), `numpy` (optional accel), and `scipy` (optional accel).
- Typical setup (venv recommended):
  - `python3 -m venv .venv`
  - `source .venv/bin/activate`
  - `python3 -m pip install -U pip`
  - `python3 -m pip install -r requirements.txt`

Lint + format (configured in `pyproject.toml`):
- Install tools:
  - `python3 -m pip install -U ruff`
- Lint:
  - `python3 -m ruff check .`
- Format:
  - `python3 -m ruff format .`

Type-check (configured in `pyproject.toml`):
- Install tools:
  - `python3 -m pip install -U mypy`
- Run:
  - `python3 -m mypy .`

Tests (checked in under `tests/`):
- Run all: `python3 -m unittest`
- Run a single file: `python3 -m unittest tests.test_path_search`
- Run a single test case:
  - `python3 -m unittest tests.test_path_search.TestFindPath.test_rectangle_tour_length`

Benchmark:
- `python3 benchmark.py --n 50 --strategy nearest_two_opt`

Quick manual sanity checks:
- Start the app and click a few points; the path should update without exceptions.
- Try `m` to cycle strategies and `a` to toggle animation.

----------------------------------------
Code Style Guidelines

General:
- Prefer small, pure functions with explicit inputs/outputs.
- Keep interactive/UI code (`pygame` loop) separate from algorithmic code.
- Avoid work at import time in library modules; use `if __name__ == "__main__":` for entrypoints.

Formatting:
- Follow PEP 8 (enforced by `ruff`).
- Keep lines readable; when in doubt, wrap at ~100 chars.

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

Naming:
- Functions/variables: `snake_case`.
- Classes: `PascalCase`.
- Constants: `UPPER_SNAKE_CASE`.

Error handling:
- Raise specific exceptions with actionable messages.
- Validate inputs at module boundaries.
- In the Pygame loop, handle quit events cleanly (`pygame.quit()` then exit).

Algorithmic performance:
- Be explicit about complexity; the brute-force TSP solver is O(n!).
- Heuristics (nearest neighbor, 2-opt) should be preferred for n > 10.
- `game_screen.py` uses a background thread for solving to keep UI responsive.

Pygame specifics:
- Keep a stable framerate (`clock.tick(60)` is fine).
- Use `_world_to_screen` / `_screen_to_world` for coordinate transforms (pan/zoom).
- Use explicit RGB tuples (or named colors) consistently.

Documentation:
- Add docstrings to any non-trivial function (especially solver functions).

Repo hygiene:
- Note: `README.md` is UTF-16 LE with CRLF; only change encoding intentionally.
- Avoid committing runtime artifacts (`__pycache__/`, `.venv/`, `*.pyc`).

----------------------------------------
Working Agreement For Agents

- Do not introduce new tooling unless necessary.
- Prefer minimal diffs.
