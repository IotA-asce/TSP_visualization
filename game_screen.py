import pygame
from path_search import find_path

def run_game():
    pygame.init()

    screen = pygame.display.set_mode((1000, 1000))

    clock = pygame.time.Clock()

    points = []
    path = []

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                # print(pos)
                points.append(pos)
                path = find_path(points=points)
        
        screen.fill("White")

        for point in points:
            pygame.draw.circle(
                surface=screen, 
                color=(0, 0, 0),
                center=point,
                radius=5
            )

        last = (0, 0)
        for point in path:
            pygame.draw.line(screen, (0, 0, 0), last, point)
            last = point

        pygame.draw.line(screen, (0,0,0), last, (0,0))

        pygame.display.flip()
        clock.tick(60)

run_game()
