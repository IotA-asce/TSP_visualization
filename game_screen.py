"""Pygame UI for collecting points and visualizing the computed route."""

from __future__ import annotations

import json
import math
import threading
import time
from pathlib import Path

try:
    import pygame
except ModuleNotFoundError as exc:  # pragma: no cover
    raise ModuleNotFoundError(
        "pygame is required to run the interactive UI; install dependencies via 'pip install -r requirements.txt'"
    ) from exc

from path_search import Strategy, find_path, find_path_step

WINDOW_SIZE = (1000, 1000)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 30, 30)
POINT_RADIUS = 5
POINT_HIT_RADIUS = 12
PATH_WIDTH = 2
ANIMATION_SPEED_EDGES_PER_S = 14.0
MIN_SCALE = 0.2
MAX_SCALE = 6.0
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


def _world_to_screen(
    pos_world: tuple[float, float],
    *,
    scale: float,
    offset: tuple[float, float],
) -> tuple[int, int]:
    x, y = pos_world
    ox, oy = offset
    return (int(round(x * scale + ox)), int(round(y * scale + oy)))


def _screen_to_world(
    pos_screen: tuple[int, int],
    *,
    scale: float,
    offset: tuple[float, float],
) -> tuple[float, float]:
    sx, sy = pos_screen
    ox, oy = offset
    return ((sx - ox) / scale, (sy - oy) / scale)


def _hit_test(
    points_world: list[tuple[float, float]],
    pos_screen: tuple[int, int],
    *,
    scale: float,
    offset: tuple[float, float],
) -> int | None:
    sx, sy = pos_screen
    best_i: int | None = None
    best_d2 = float("inf")
    for i, p in enumerate(points_world):
        px, py = _world_to_screen(p, scale=scale, offset=offset)
        d2 = (px - sx) ** 2 + (py - sy) ** 2
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

    # Attempt to initialize font module, but handle broken installations (e.g. Python 3.14 + pygame 2.6.1 circular import)
    font = None
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            if not pygame.font.get_init():
                pygame.font.init()
            font = pygame.font.Font(None, 22)
    except Exception:
        font = None

    window_size = WINDOW_SIZE
    points: list[tuple[float, float]] = []
    path: list[tuple[float, float]] = []
    dragging_index: int | None = None

    screen = pygame.display.set_mode(window_size, pygame.RESIZABLE)
    pygame.display.set_caption("TSP Visualization")
    clock = pygame.time.Clock()

    try:
        strategy_index = STRATEGIES.index(strategy)
    except ValueError:
        strategy_index = 0

    status: str | None = None
    status_until = 0.0
    export_path: Path | None = None
    animate = True
    step_by_step = False  # Toggle for visualizing solver steps
    draw_progress = 0.0

    compute_lock = threading.Lock()
    compute_request_id = 0
    computing = False

    view_scale = 1.0
    view_offset = (0.0, 0.0)
    panning = False
    pan_start_mouse = (0, 0)
    pan_start_offset = (0.0, 0.0)

    # Human vs Solver Mode State
    human_mode = False
    user_route: list[int] = []
    solver_best_len: float = 0.0

    # Untangle Game Mode State
    untangle_mode = False
    untangle_path: list[int] = []
    untangle_target: float = 0.0
    untangle_selected_edge: int | None = None  # index in untangle_path

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

        nonlocal compute_request_id
        nonlocal computing

        points_snapshot = list(points)
        closed_snapshot = closed
        strategy_snapshot = STRATEGIES[strategy_index]

        if len(points_snapshot) < 2:
            path = list(points_snapshot)
            draw_progress = 0.0
            return

        with compute_lock:
            compute_request_id += 1
            request_id = compute_request_id
            computing = True

        def worker() -> None:
            nonlocal path
            nonlocal draw_progress
            nonlocal computing

            t0 = time.perf_counter()
            try:
                if step_by_step:
                    # Generator mode for visualization
                    gen = find_path_step(
                        points=points_snapshot,
                        closed=closed_snapshot,
                        strategy=strategy_snapshot,
                    )

                    final_path = []
                    step_count = 0

                    for step_path in gen:
                        with compute_lock:
                            if request_id != compute_request_id:
                                return
                            path = step_path
                            draw_progress = float(len(path))  # Show full path immediately

                        step_count += 1
                        # Throttle updates slightly to make them visible
                        time.sleep(0.05)

                    final_path = path  # Last yielded path is the result

                    with compute_lock:
                        if request_id != compute_request_id:
                            return
                        computing = False

                    elapsed_ms = (time.perf_counter() - t0) * 1000.0
                    set_status(f"visualized {step_count} steps in {elapsed_ms:.1f} ms")

                else:
                    # Standard atomic update
                    new_path = find_path(
                        points=points_snapshot,
                        closed=closed_snapshot,
                        strategy=strategy_snapshot,
                    )

                    elapsed_ms = (time.perf_counter() - t0) * 1000.0
                    with compute_lock:
                        if request_id != compute_request_id:
                            return
                        path = new_path
                        draw_progress = 0.0
                        computing = False
                    set_status(f"computed in {elapsed_ms:.1f} ms")

            except Exception as exc:
                with compute_lock:
                    if request_id != compute_request_id:
                        return
                    computing = False
                set_status(f"solver error: {exc}")
                return

        threading.Thread(target=worker, daemon=True).start()

    if initial_points:
        points.extend([(float(x), float(y)) for (x, y) in initial_points])
        recompute_path()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.VIDEORESIZE:
                old_w, old_h = window_size
                center_world = _screen_to_world(
                    (old_w // 2, old_h // 2),
                    scale=view_scale,
                    offset=view_offset,
                )
                window_size = (event.w, event.h)
                screen = pygame.display.set_mode(window_size, pygame.RESIZABLE)
                new_w, new_h = window_size
                view_offset = (
                    (new_w / 2) - center_world[0] * view_scale,
                    (new_h / 2) - center_world[1] * view_scale,
                )

            if event.type == pygame.MOUSEWHEEL:
                mx, my = pygame.mouse.get_pos()
                wx, wy = _screen_to_world((mx, my), scale=view_scale, offset=view_offset)
                zoom = 1.1**event.y
                new_scale = max(MIN_SCALE, min(MAX_SCALE, view_scale * zoom))
                new_offset = (mx - wx * new_scale, my - wy * new_scale)
                view_scale = new_scale
                view_offset = new_offset

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
                elif event.key == pygame.K_v:
                    step_by_step = not step_by_step
                    status_msg = (
                        "Step-by-Step Visualization: ON"
                        if step_by_step
                        else "Step-by-Step Visualization: OFF"
                    )
                    set_status(status_msg)
                    if step_by_step:
                        recompute_path()
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
                elif event.key == pygame.K_h:
                    if len(points) >= 3:
                        human_mode = not human_mode
                        if human_mode:
                            user_route = []
                            # Capture the current solver length as the target
                            solver_best_len = _path_length(path, closed=closed)
                            set_status("Human Mode: Click points to connect them")
                        else:
                            set_status("Exited Human Mode")
                    else:
                        set_status("Need at least 3 points for Human Mode")
                elif event.key == pygame.K_u:
                    if len(points) >= 4:
                        untangle_mode = not untangle_mode
                        if untangle_mode:
                            # Generate a random shuffled path
                            import random

                            untangle_path = list(range(len(points)))
                            random.shuffle(untangle_path)
                            untangle_selected_edge = None

                            # Calculate target using the solver
                            target_pts = find_path(points, closed=closed, strategy="auto")
                            untangle_target = _path_length(target_pts, closed=closed)

                            set_status("Untangle Mode: Click edges to swap them")
                        else:
                            set_status("Exited Untangle Mode")
                    else:
                        set_status("Need at least 4 points for Untangle Mode")

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                panning = True
                pan_start_mouse = pygame.mouse.get_pos()
                pan_start_offset = view_offset

            if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                panning = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_screen = pygame.mouse.get_pos()
                hit = _hit_test(points, mouse_screen, scale=view_scale, offset=view_offset)

                if human_mode:
                    if hit is not None:
                        # Logic for building user path
                        if hit not in user_route:
                            user_route.append(hit)
                        elif closed and len(user_route) == len(points) and hit == user_route[0]:
                            # Allow closing the loop by clicking the first point again
                            pass
                elif untangle_mode:
                    # Logic for selecting edges to swap
                    mx, my = mouse_screen
                    best_edge_idx = None
                    best_edge_dist = 10.0  # hit threshold in pixels

                    n = len(untangle_path)
                    for i in range(n):
                        if not closed and i == n - 1:
                            break

                        idx1 = untangle_path[i]
                        idx2 = untangle_path[(i + 1) % n]
                        p1 = _world_to_screen(points[idx1], scale=view_scale, offset=view_offset)
                        p2 = _world_to_screen(points[idx2], scale=view_scale, offset=view_offset)

                        # Distance from point (mx, my) to line segment p1-p2
                        x1, y1 = p1
                        x2, y2 = p2

                        dx = x2 - x1
                        dy = y2 - y1
                        if dx == 0 and dy == 0:
                            continue

                        # Project point onto line (parameter t)
                        t = ((mx - x1) * dx + (my - y1) * dy) / (dx * dx + dy * dy)
                        t = max(0, min(1, t))

                        closest_x = x1 + t * dx
                        closest_y = y1 + t * dy

                        dist = math.hypot(mx - closest_x, my - closest_y)
                        if dist < best_edge_dist:
                            best_edge_dist = dist
                            best_edge_idx = i

                    if best_edge_idx is not None:
                        if untangle_selected_edge is None:
                            untangle_selected_edge = best_edge_idx
                        else:
                            # Perform 2-opt swap logic
                            i = untangle_selected_edge
                            j = best_edge_idx

                            if i > j:
                                i, j = j, i

                            # Valid swap condition for 2-opt
                            if i != j and (closed or (i > 0 and j < n - 1)):
                                # Reverses the segment between i+1 and j
                                # untangle_path[i+1 : j+1] = reversed(untangle_path[i+1 : j+1])
                                # Python slice assignment handles the reversal
                                new_segment = untangle_path[i + 1 : j + 1]
                                new_segment.reverse()
                                untangle_path[i + 1 : j + 1] = new_segment

                            untangle_selected_edge = None
                else:
                    if hit is None:
                        points.append(
                            _screen_to_world(
                                mouse_screen,
                                scale=view_scale,
                                offset=view_offset,
                            )
                        )
                        recompute_path()
                    else:
                        dragging_index = hit

            if event.type == pygame.MOUSEMOTION and panning:
                mx, my = pygame.mouse.get_pos()
                sx, sy = pan_start_mouse
                ox, oy = pan_start_offset
                view_offset = (ox + (mx - sx), oy + (my - sy))

            if event.type == pygame.MOUSEMOTION and dragging_index is not None and not panning:
                points[dragging_index] = _screen_to_world(
                    pygame.mouse.get_pos(),
                    scale=view_scale,
                    offset=view_offset,
                )

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
                center=_world_to_screen(point, scale=view_scale, offset=view_offset),
                radius=POINT_RADIUS,
            )

        if len(path) >= 2 and not human_mode and not untangle_mode:
            edges: list[tuple[tuple[float, float], tuple[float, float]]] = []
            for a, b in zip(path, path[1:]):
                edges.append((a, b))
            if closed:
                edges.append((path[-1], path[0]))

            # ... (animation logic remains here) ...
            if animate:
                full_edges = min(int(draw_progress), len(edges))
                frac = min(max(draw_progress - full_edges, 0.0), 1.0)

                for i in range(full_edges):
                    a, b = edges[i]
                    pygame.draw.line(
                        screen,
                        BLACK,
                        _world_to_screen(a, scale=view_scale, offset=view_offset),
                        _world_to_screen(b, scale=view_scale, offset=view_offset),
                        width=PATH_WIDTH,
                    )
                    pygame.draw.aaline(
                        screen,
                        BLACK,
                        _world_to_screen(a, scale=view_scale, offset=view_offset),
                        _world_to_screen(b, scale=view_scale, offset=view_offset),
                    )

                if full_edges < len(edges) and frac > 0.0:
                    a, b = edges[full_edges]
                    x = a[0] + (b[0] - a[0]) * frac
                    y = a[1] + (b[1] - a[1]) * frac
                    mid = (x, y)
                    pygame.draw.line(
                        screen,
                        BLACK,
                        _world_to_screen(a, scale=view_scale, offset=view_offset),
                        _world_to_screen(mid, scale=view_scale, offset=view_offset),
                        width=PATH_WIDTH,
                    )
                    pygame.draw.aaline(
                        screen,
                        BLACK,
                        _world_to_screen(a, scale=view_scale, offset=view_offset),
                        _world_to_screen(mid, scale=view_scale, offset=view_offset),
                    )
            else:
                for a, b in edges:
                    pygame.draw.line(
                        screen,
                        BLACK,
                        _world_to_screen(a, scale=view_scale, offset=view_offset),
                        _world_to_screen(b, scale=view_scale, offset=view_offset),
                        width=PATH_WIDTH,
                    )
                    pygame.draw.aaline(
                        screen,
                        BLACK,
                        _world_to_screen(a, scale=view_scale, offset=view_offset),
                        _world_to_screen(b, scale=view_scale, offset=view_offset),
                    )

        if human_mode and len(user_route) >= 2:
            BLUE = (0, 0, 255)
            # Draw user edges
            for i in range(len(user_route) - 1):
                idx1 = user_route[i]
                idx2 = user_route[i + 1]
                p1 = points[idx1]
                p2 = points[idx2]
                pygame.draw.line(
                    screen,
                    BLUE,
                    _world_to_screen(p1, scale=view_scale, offset=view_offset),
                    _world_to_screen(p2, scale=view_scale, offset=view_offset),
                    width=PATH_WIDTH,
                )

            # Draw closing edge if completed
            if closed and len(user_route) == len(points):
                idx1 = user_route[-1]
                idx2 = user_route[0]
                p1 = points[idx1]
                p2 = points[idx2]
                pygame.draw.line(
                    screen,
                    BLUE,
                    _world_to_screen(p1, scale=view_scale, offset=view_offset),
                    _world_to_screen(p2, scale=view_scale, offset=view_offset),
                    width=PATH_WIDTH,
                )

        if untangle_mode and len(untangle_path) >= 2:
            # Draw untangle edges
            ORANGE = (255, 165, 0)
            SELECTED = (255, 0, 255)  # Magenta

            n = len(untangle_path)
            for i in range(n):
                if not closed and i == n - 1:
                    break

                idx1 = untangle_path[i]
                idx2 = untangle_path[(i + 1) % n]
                p1 = points[idx1]
                p2 = points[idx2]

                color = SELECTED if i == untangle_selected_edge else ORANGE
                width = PATH_WIDTH + 2 if i == untangle_selected_edge else PATH_WIDTH

                pygame.draw.line(
                    screen,
                    color,
                    _world_to_screen(p1, scale=view_scale, offset=view_offset),
                    _world_to_screen(p2, scale=view_scale, offset=view_offset),
                    width=width,
                )

        mode = "closed" if closed else "open"
        strategy = STRATEGIES[strategy_index]
        length = _path_length(path, closed=closed)

        if human_mode:
            user_len = 0.0
            if len(user_route) > 1:
                user_path_pts = [points[i] for i in user_route]
                user_len = _path_length(
                    user_path_pts, closed=(closed and len(user_route) == len(points))
                )

            score_str = ""
            if closed and len(user_route) == len(points) and user_len > 0:
                ratio = (solver_best_len / user_len) * 100
                score_str = f"  AI: {solver_best_len:.1f}  Score: {ratio:.1f}%"

            hud = f"HUMAN MODE: {len(user_route)}/{len(points)}  User: {user_len:.1f}{score_str}"
        elif untangle_mode:
            current_len = 0.0
            if untangle_path:
                pts = [points[i] for i in untangle_path]
                current_len = _path_length(pts, closed=closed)

            diff = (current_len / untangle_target) * 100 if untangle_target > 0 else 0
            hud = (
                f"UNTANGLE: Target: {untangle_target:.1f}  Current: {current_len:.1f} ({diff:.1f}%)"
            )
        else:
            hud = f"points: {len(points)}  {mode}  {strategy}  length: {length:.1f}  zoom: {view_scale:.2f}"

        if font:
            screen.blit(font.render(hud, True, BLACK), HUD_POS)

        hint: str | None = None
        if strategy == "bruteforce" and len(points) > 10:
            hint = "warning: bruteforce is O(n!) and may freeze for n > 10"
        elif len(points) > 200:
            hint = "hint: large point counts may be slow; try 'nearest_two_opt'"

        if status is not None and time.time() <= status_until:
            if font:
                screen.blit(font.render(status, True, BLACK), HUD_STATUS_POS)
        elif computing:
            if font:
                screen.blit(font.render("computing...", True, BLACK), HUD_STATUS_POS)

        if hint is not None:
            if font:
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
