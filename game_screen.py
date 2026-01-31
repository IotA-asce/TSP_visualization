"""Pygame UI for collecting points and visualizing the computed route."""

from __future__ import annotations

import json
import math
import time
from pathlib import Path

try:
    import pygame
except ModuleNotFoundError as exc:  # pragma: no cover
    raise ModuleNotFoundError(
        "pygame is required to run the interactive UI; install dependencies via 'pip install -r requirements.txt'"
    ) from exc

from path_search import Strategy, find_path

WINDOW_SIZE = (1000, 1000)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 30, 30)
POINT_RADIUS = 5
POINT_HIT_RADIUS = 12
PATH_WIDTH = 2
ANIMATION_SPEED_EDGES_PER_S = 14.0
HUD_POS = (10, 10)
HUD_STATUS_POS = (10, 32)
HUD_HINT_POS = (10, 54)

SAVE_PATH = Path("points.json")
EXPORT_PREFIX = "export"
DATA_DIR = Path(__file__).resolve().parent / "data"
DEMO_SMALL_PATH = DATA_DIR / "small.json"
DEMO_MEDIUM_PATH = DATA_DIR / "medium.json"

STRATEGIES: list[Strategy] = [
    "auto",
    "nearest_two_opt",
    "nearest",
    "two_opt",
    "bruteforce",
]


def _to_point(pos: tuple[int, int]) -> tuple[float, float]:
    x, y = pos
    return (float(x), float(y))


def _to_screen(pos: tuple[float, float]) -> tuple[int, int]:
    x, y = pos
    return (int(round(x)), int(round(y)))


def _hit_test(points: list[tuple[float, float]], pos: tuple[float, float]) -> int | None:
    x, y = pos
    best_i: int | None = None
    best_d2 = float("inf")
    for i, (px, py) in enumerate(points):
        d2 = (px - x) ** 2 + (py - y) ** 2
        if d2 <= POINT_HIT_RADIUS**2 and d2 < best_d2:
            best_d2 = d2
            best_i = i
    return best_i


def _path_length(path: list[tuple[float, float]], *, closed: bool) -> float:
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


def run_game(
    *,
    initial_points: list[tuple[float, float]] | None = None,
    closed: bool = True,
    strategy: Strategy = "auto",
) -> None:
    pygame.init()

    screen = pygame.display.set_mode(WINDOW_SIZE)
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 22)

    points: list[tuple[float, float]] = []
    path: list[tuple[float, float]] = []
    dragging_index: int | None = None

    try:
        strategy_index = STRATEGIES.index(strategy)
    except ValueError:
        strategy_index = 0

    status: str | None = None
    status_until = 0.0
    export_path: Path | None = None
    animate = True
    draw_progress = 0.0

    def set_status(message: str, *, seconds: float = 2.0) -> None:
        nonlocal status, status_until
        status = message
        status_until = time.time() + seconds

    def save_state() -> None:
        data = {
            "points": [[x, y] for (x, y) in points],
            "closed": closed,
            "strategy": STRATEGIES[strategy_index],
        }
        SAVE_PATH.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        set_status(f"saved {len(points)} points -> {SAVE_PATH}")

    def load_state(path: Path) -> None:
        nonlocal closed, strategy_index, dragging_index
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            set_status(f"missing {path}")
            return
        except json.JSONDecodeError:
            set_status(f"invalid json in {path}")
            return

        raw_points = data.get("points")
        if not isinstance(raw_points, list):
            set_status(f"invalid format in {path}")
            return

        loaded_points: list[tuple[float, float]] = []
        for p in raw_points:
            if not isinstance(p, list) or len(p) != 2:
                set_status(f"invalid point in {path}")
                return
            loaded_points.append((float(p[0]), float(p[1])))

        points.clear()
        points.extend(loaded_points)

        closed = bool(data.get("closed", True))
        loaded_strategy = data.get("strategy", "auto")
        if loaded_strategy in STRATEGIES:
            strategy_index = STRATEGIES.index(loaded_strategy)
        else:
            strategy_index = 0

        dragging_index = None
        recompute_path()
        set_status(f"loaded {len(points)} points <- {path}")

    def recompute_path() -> None:
        nonlocal path
        nonlocal draw_progress
        path = find_path(
            points=points,
            closed=closed,
            strategy=STRATEGIES[strategy_index],
        )
        draw_progress = 0.0

    if initial_points:
        points.extend([(float(x), float(y)) for (x, y) in initial_points])
        recompute_path()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    if points:
                        points.pop()
                        recompute_path()
                elif event.key == pygame.K_c:
                    points.clear()
                    path.clear()
                    dragging_index = None
                elif event.key == pygame.K_r:
                    recompute_path()
                elif event.key == pygame.K_t:
                    closed = not closed
                    recompute_path()
                elif event.key == pygame.K_m:
                    strategy_index = (strategy_index + 1) % len(STRATEGIES)
                    recompute_path()
                elif event.key == pygame.K_a:
                    animate = not animate
                    draw_progress = 0.0
                elif event.key == pygame.K_s:
                    save_state()
                elif event.key == pygame.K_l:
                    load_state(SAVE_PATH)
                elif event.key == pygame.K_1:
                    load_state(DEMO_SMALL_PATH)
                elif event.key == pygame.K_2:
                    load_state(DEMO_MEDIUM_PATH)
                elif event.key == pygame.K_e:
                    export_path = Path(f"{EXPORT_PREFIX}_{time.strftime('%Y%m%d_%H%M%S')}.png")
                    set_status(f"exporting -> {export_path}")

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse = _to_point(pygame.mouse.get_pos())
                hit = _hit_test(points, mouse)
                if hit is None:
                    points.append(mouse)
                    recompute_path()
                else:
                    dragging_index = hit

            if event.type == pygame.MOUSEMOTION and dragging_index is not None:
                points[dragging_index] = _to_point(pygame.mouse.get_pos())

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if dragging_index is not None:
                    dragging_index = None
                    recompute_path()

        screen.fill(WHITE)

        for point in points:
            color = BLACK
            if point == path[0] if path else False:
                color = RED
            pygame.draw.circle(
                surface=screen,
                color=color,
                center=_to_screen(point),
                radius=POINT_RADIUS,
            )

        if len(path) >= 2:
            edges: list[tuple[tuple[float, float], tuple[float, float]]] = []
            for a, b in zip(path, path[1:]):
                edges.append((a, b))
            if closed:
                edges.append((path[-1], path[0]))

            if animate:
                full_edges = min(int(draw_progress), len(edges))
                frac = min(max(draw_progress - full_edges, 0.0), 1.0)

                for i in range(full_edges):
                    a, b = edges[i]
                    pygame.draw.line(
                        screen,
                        BLACK,
                        _to_screen(a),
                        _to_screen(b),
                        width=PATH_WIDTH,
                    )
                    pygame.draw.aaline(screen, BLACK, _to_screen(a), _to_screen(b))

                if full_edges < len(edges) and frac > 0.0:
                    a, b = edges[full_edges]
                    x = a[0] + (b[0] - a[0]) * frac
                    y = a[1] + (b[1] - a[1]) * frac
                    mid = (x, y)
                    pygame.draw.line(
                        screen,
                        BLACK,
                        _to_screen(a),
                        _to_screen(mid),
                        width=PATH_WIDTH,
                    )
                    pygame.draw.aaline(screen, BLACK, _to_screen(a), _to_screen(mid))
            else:
                for a, b in edges:
                    pygame.draw.line(
                        screen,
                        BLACK,
                        _to_screen(a),
                        _to_screen(b),
                        width=PATH_WIDTH,
                    )
                    pygame.draw.aaline(screen, BLACK, _to_screen(a), _to_screen(b))

        mode = "closed" if closed else "open"
        strategy = STRATEGIES[strategy_index]
        length = _path_length(path, closed=closed)
        hud = f"points: {len(points)}  {mode}  {strategy}  length: {length:.1f}"
        screen.blit(font.render(hud, True, BLACK), HUD_POS)

        hint: str | None = None
        if strategy == "bruteforce" and len(points) > 10:
            hint = "warning: bruteforce is O(n!) and may freeze for n > 10"
        elif len(points) > 200:
            hint = "hint: large point counts may be slow; try 'nearest_two_opt'"

        if status is not None and time.time() <= status_until:
            screen.blit(font.render(status, True, BLACK), HUD_STATUS_POS)

        if hint is not None:
            screen.blit(font.render(hint, True, BLACK), HUD_HINT_POS)

        if export_path is not None:
            try:
                pygame.image.save(screen, str(export_path))
            except Exception:
                set_status(f"failed to export -> {export_path}")
            else:
                set_status(f"exported -> {export_path}")
            export_path = None

        pygame.display.flip()

        dt_s = clock.tick(60) / 1000.0
        if animate and len(path) >= 2:
            draw_progress += ANIMATION_SPEED_EDGES_PER_S * dt_s


if __name__ == "__main__":
    run_game()
