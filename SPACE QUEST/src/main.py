import pygame
from config import *
from clases import *

crear_tabla_puntuaciones()

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Quest")

main_menu = MainMenu()
game = Game()
game_over_menu = GameOverMenu()
level_selector = LevelSelector(levels_data)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    main_menu.display_menu(screen)
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            if main_menu.play_rect.collidepoint(event.pos):
                level_selector.draw(screen)
                pygame.display.flip()
                level_selector.handle_events()
                level_selected = level_selector.selected_level
                if level_selected is not None:
                    game.set_level_parameters(level_selected)
                    game.start_game(screen)
            elif main_menu.exit_rect.collidepoint(event.pos):
                running = False
        elif event.type == pygame.QUIT:
            running = False
