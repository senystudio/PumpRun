import os
import pygame
import pygame_menu
import time


def terminate():
    pygame.quit()
    exit()


def run_menu():
    def start_game():
        os.startfile(""'level_copy.exe'"")

    def start_game2():
        os.startfile(""'level_copy2.exe'"")

    def start_game_core():
        start_game()
        terminate()

    def start_game_core2():
        start_game2()
        terminate()

    menu = pygame_menu.Menu(title='PumpRun',
                            width=monitor_size[0], height=monitor_size[1],
                            theme=theme)
    menu.add.button('START GAME ( LEVEL 1 )', start_game_core)
    menu.add.button('START GAME ( LEVEL 2 )', start_game_core2)

    menu.add.button('QUIT', pygame_menu.events.EXIT)

    while True:
        clock.tick(FPS)
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                terminate()
        menu.draw(display)
        menu.update(events)

        pygame.display.flip()


ACT_RECOUNT_EVENT = pygame.USEREVENT + 1

pygame.init()

pygame.time.set_timer(ACT_RECOUNT_EVENT, 500)

FPS = 60

monitor_size = [pygame.display.Info().current_w, pygame.display.Info().current_h]
DISPLAY_S = min(monitor_size)
display = pygame.display.set_mode(monitor_size, display=0)

clock = pygame.time.Clock()

theme = pygame_menu.themes.THEME_GREEN.copy()
theme.title_background_color = 50, 50, 50
theme.title_font_color = 59, 215, 5
theme.title_font_shadow = False
theme.title_font = pygame_menu.font.FONT_BEBAS

theme.widget_font_size = 40
theme.background_color = 173, 100, 1
theme.widget_font_color = 139, 69, 19
theme.selection_color = 255, 236, 20
theme.widget_selection_effect = pygame_menu.widgets.selection.LeftArrowSelection()
theme.widget_font = pygame_menu.font.FONT_8BIT

run_menu()
