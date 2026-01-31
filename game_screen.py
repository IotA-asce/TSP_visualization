"""Pygame UI for collecting points and visualizing the computed route."""

from __future__ import annotations

import math

import pygame

from path_search import Strategy, find_path

WINDOW_SIZE = (1000, 1000)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 30, 30)
POINT_RADIUS = 5
POINT_HIT_RADIUS = 12
PATH_WIDTH = 2
HUD_POS = (10, 10)

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


def run_game() -> None:
    pygame.init()

    screen = pygame.display.set_mode(WINDOW_SIZE)
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 22)

    points: list[tuple[float, float]] = []
    path: list[tuple[float, float]] = []
    dragging_index: int | None = None

    closed = True
    strategy_index = 0

    def recompute_path() -> None:
        nonlocal path
        path = find_path(
            points=points,
            closed=closed,
            strategy=STRATEGIES[strategy_index],
        )

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
            last = path[0]
            for point in path[1:]:
                pygame.draw.line(
                    screen,
                    BLACK,
                    _to_screen(last),
                    _to_screen(point),
                    width=PATH_WIDTH,
                )
                pygame.draw.aaline(screen, BLACK, _to_screen(last), _to_screen(point))
                last = point
            if closed:
                pygame.draw.line(
                    screen,
                    BLACK,
                    _to_screen(last),
                    _to_screen(path[0]),
                    width=PATH_WIDTH,
                )
                pygame.draw.aaline(screen, BLACK, _to_screen(last), _to_screen(path[0]))

        mode = "closed" if closed else "open"
        strategy = STRATEGIES[strategy_index]
        length = _path_length(path, closed=closed)
        hud = f"points: {len(points)}  {mode}  {strategy}  length: {length:.1f}"
        screen.blit(font.render(hud, True, BLACK), HUD_POS)

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    run_game()
