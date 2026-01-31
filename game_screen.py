"""Pygame UI for collecting points and visualizing the computed route."""

from __future__ import annotations

import pygame

from path_search import find_path

WINDOW_SIZE = (1000, 1000)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
POINT_RADIUS = 5


def run_game() -> None:
    pygame.init()

    screen = pygame.display.set_mode(WINDOW_SIZE)
    clock = pygame.time.Clock()

    points: list[tuple[int, int]] = []
    path: list[tuple[int, int]] = []

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                points.append(pos)
                path = find_path(points=points)

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

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    run_game()
