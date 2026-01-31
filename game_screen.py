"""Pygame UI for collecting points and visualizing the computed route."""

from __future__ import annotations

import math

import pygame

from path_search import find_path

WINDOW_SIZE = (1000, 1000)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
POINT_RADIUS = 5
HUD_POS = (10, 10)


def _tour_length(path: list[tuple[float, float]]) -> float:
    if len(path) < 2:
        return 0.0

    total = 0.0
    for i in range(len(path)):
        x1, y1 = path[i]
        x2, y2 = path[(i + 1) % len(path)]
        total += math.hypot(x2 - x1, y2 - y1)
    return total


def run_game() -> None:
    pygame.init()

    screen = pygame.display.set_mode(WINDOW_SIZE)
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 22)

    points: list[tuple[float, float]] = []
    path: list[tuple[float, float]] = []

    def recompute_path() -> None:
        nonlocal path
        path = find_path(points=points)

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
                elif event.key == pygame.K_r:
                    recompute_path()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                points.append(pygame.mouse.get_pos())
                recompute_path()

        screen.fill(WHITE)

        for point in points:
            pygame.draw.circle(
                surface=screen,
                color=BLACK,
                center=point,
                radius=POINT_RADIUS,
            )

        if len(path) >= 2:
            last = path[0]
            for point in path[1:]:
                pygame.draw.line(screen, BLACK, last, point)
                last = point
            pygame.draw.line(screen, BLACK, last, path[0])

        hud = f"points: {len(points)}  tour length: {_tour_length(path):.1f}"
        screen.blit(font.render(hud, True, BLACK), HUD_POS)

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    run_game()
