# Title: Main Battleship Test
# Author: Nathan Vallad
# Date: 11/17/2025
# Purpose: Test the Ship and Board classes using Pygame. Allows placing ships on the board
# and firing shots by clicking cells. Displays hits, misses, and sunk ships visually.

# Date: 12/01/2025
# Purpose: Run a playable test of Battleship using Pygame.
# Player can place ships, AI auto-places ships, and the game
# logic handles turns, firing, and win detection.

# main.py
import pygame
import sys
import multiprocessing
from pvp_window import run_pvp
from pvp_shared import init_shared_state
from ai_window import run_ai

# CONFIG 
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 400
BLACK = (20, 20, 20)
WHITE = (240, 240, 240)
GREEN = (60, 200, 80)
YELLOW = (230, 200, 40)

def init_menu():
    """Initialize pygame and menu display."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Battleship Menu")
    font = pygame.font.SysFont(None, 32)
    clock = pygame.time.Clock()
    return screen, font, clock


screen, font, clock = init_menu()


def draw_menu(selected):
    screen.fill(BLACK)
    title = font.render("BATTLESHIP", True, YELLOW)
    screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))

    options = ["Player vs Player", "Player vs Computer", "Quit"]
    for i, text in enumerate(options):
        color = GREEN if i == selected else WHITE
        surf = font.render(text, True, color)
        screen.blit(surf, (SCREEN_WIDTH//2 - surf.get_width()//2, 150 + i*60))

    pygame.display.flip()


def run_menu():
    selected = 0
    while True:
        draw_menu(selected)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % 3
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % 3
                elif event.key == pygame.K_RETURN:
                    return ["pvp", "ai", "quit"][selected]
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                for i in range(3):
                    if 150 + i*60 <= my <= 150 + i*60 + 32:
                        return ["pvp", "ai", "quit"][i]

        clock.tick(60)


if __name__ == "__main__":
    while True:
        # Reinitialize pygame and menu for each loop (in case game quit pygame)
        if not pygame.display.get_surface():
            screen, font, clock = init_menu()
        
        mode = run_menu()

        if mode == "quit":
            pygame.quit()
            sys.exit()

        elif mode == "pvp":
            # Run PvP with shared state via multiprocessing.Manager
            # Loop allows "Play Again" to restart without closing menu
            while True:
                with multiprocessing.Manager() as manager:
                    shared_state = manager.dict(init_shared_state())
                    p1 = multiprocessing.Process(target=run_pvp, args=(1, shared_state))
                    p2 = multiprocessing.Process(target=run_pvp, args=(2, shared_state))
                    p1.start()
                    p2.start()
                    p1.join()
                    p2.join()
                
                # If both processes ended normally, break and return to menu
                # (If user clicked "Quit" in popup, sys.exit() would have been called)
                break

        elif mode == "ai":
            # Loop allows "Play Again" to restart without closing menu
            while True:
                run_ai()
                # If run_ai() returns normally, break and return to menu
                # (If user clicked "Quit" in popup, sys.exit() would have been called)
                break
