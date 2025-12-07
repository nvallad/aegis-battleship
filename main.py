# Title: Main Battleship Test
# Author: Nathan Vallad
# Date: 11/17/2025
# Purpose: Test the Ship and Board classes using Pygame. Allows placing ships on the board
# and firing shots by clicking cells. Displays hits, misses, and sunk ships visually.

# Date: 12/01/2025
# Purpose: Run a playable test of Battleship using Pygame.
# Player can place ships, AI auto-places ships, and the game
# logic handles turns, firing, and win detection.

import pygame
from board import Board
from ship import Ship
from player import Player
from AI import AI
from game_logic import GameLogic

# ------------------- CONFIG -------------------
ROWS, COLS = 10, 10
CELL_SIZE = 40
PADDING = 20

SCREEN_WIDTH = 2 * (COLS * CELL_SIZE) + 3 * PADDING
SCREEN_HEIGHT = ROWS * CELL_SIZE + 2 * PADDING

# Colors
BLUE = (30, 144, 255)
GRAY = (120, 120, 120)
RED = (220, 40, 40)
WHITE = (240, 240, 240)
BLACK = (20, 20, 20)
GREEN = (60, 200, 80)
YELLOW = (230, 200, 40)
PREVIEW_ALPHA = 140

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Battleship Test")
font = pygame.font.SysFont(None, 24)
clock = pygame.time.Clock()

# ------------------- CREATE PLAYERS -------------------
player_board = Board(ROWS, COLS)
player = Player("Human", player_board)

ai_board = Board(ROWS, COLS)
ai_player = Player("CPU", ai_board)
ai_player.is_ai = True
ai_player.ai = AI(ai_player, difficulty="easy")

# ------------------- GAME LOGIC -------------------
game = GameLogic(player, ai_player)
game.auto_place_ships_if_ai()

# Ships to place
ships_to_place = [
    Ship("Carrier", 5),
    Ship("Battleship", 4),
    Ship("Cruiser", 3),
    Ship("Submarine", 3),
    Ship("Destroyer", 2)
]

placing_ships = True
current_ship_index = 0
orientation = "H"  # 'H' or 'V'

# ------------------- HELPER FUNCTIONS -------------------
def get_tile_from_mouse(pos, offset_x):
    x, y = pos
    col = (x - offset_x) // CELL_SIZE
    row = (y - PADDING) // CELL_SIZE
    return row, col

def draw_board(board, offset_x, reveal_ships=True, highlight=None):
    for r in range(board.rows):
        for c in range(board.cols):
            rect = pygame.Rect(offset_x + c*CELL_SIZE, PADDING + r*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            cell = board.grid[r][c]
            color = BLUE
            if cell == "S" and reveal_ships:
                color = GRAY
            elif cell == "X":
                color = RED
            elif cell == "O":
                color = WHITE
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)

    # Draw ship placement preview
    if highlight:
        s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        s.fill((GREEN[0], GREEN[1], GREEN[2], PREVIEW_ALPHA))
        for (r, c) in highlight['coords']:
            if 0 <= r < board.rows and 0 <= c < board.cols:
                rect = pygame.Rect(offset_x + c*CELL_SIZE, PADDING + r*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                screen.blit(s, (rect.x, rect.y))

def draw_ui():
    # Titles
    screen.blit(font.render("Player Board", True, YELLOW), (PADDING, 5))
    screen.blit(font.render("AI Board", True, YELLOW), (COLS*CELL_SIZE + 2*PADDING, 5))

    if placing_ships and current_ship_index < len(ships_to_place):
        s = ships_to_place[current_ship_index]
        screen.blit(font.render(f"Place {s.name} (size {s.size}) - Orientation: {orientation}", True, WHITE), (PADDING, SCREEN_HEIGHT - 30))
    elif game.is_game_over():
        screen.blit(font.render(f"Game Over! Winner: {game.get_current_player().name}", True, WHITE), (PADDING, SCREEN_HEIGHT - 30))
    else:
        screen.blit(font.render(f"{game.get_current_player().name}'s Turn", True, WHITE), (PADDING, SCREEN_HEIGHT - 30))

# ------------------- MAIN LOOP -------------------
running = True
while running:
    screen.fill(BLACK)
    mouse_pos = pygame.mouse.get_pos()
    highlight = None

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Rotate ship during placement
        if placing_ships and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                orientation = "V" if orientation == "H" else "H"

        # Mouse click
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if placing_ships:
                row, col = get_tile_from_mouse(event.pos, PADDING)
                if 0 <= row < ROWS and 0 <= col < COLS:
                    ship = ships_to_place[current_ship_index]
                    success = player.add_ship(ship, (row, col), orientation)
                    if success:
                        current_ship_index += 1
                        if current_ship_index >= len(ships_to_place):
                            placing_ships = False
            else:
                # Player fires at AI board
                row, col = get_tile_from_mouse(event.pos, COLS*CELL_SIZE + 2*PADDING)
                if 0 <= row < ROWS and 0 <= col < COLS:
                    result = game.fire(row, col)
                    print("FIRE RESULT:", result)
                    # AI automatically takes turn if needed
                    if game.get_current_player().is_ai and not game.is_game_over():
                        ai_result = game.ai_take_turn()
                        print("AI RESULT:", ai_result)

    # Highlight preview during placement
    if placing_ships and current_ship_index < len(ships_to_place):
        pr, pc = get_tile_from_mouse(mouse_pos, PADDING)
        ship = ships_to_place[current_ship_index]
        coords = []
        valid = True
        for i in range(ship.size):
            rr = pr + (i if orientation == "V" else 0)
            cc = pc + (i if orientation == "H" else 0)
            coords.append((rr, cc))
            # bounds
            if rr >= ROWS or cc >= COLS:
                valid = False
            for s in player.board.ships:
                if (rr, cc) in s.positions:
                    valid = False
        highlight = {'coords': coords, 'valid': valid}

    # Draw boards
    draw_board(player.board, PADDING, reveal_ships=True, highlight=highlight)
    draw_board(ai_player.board, COLS*CELL_SIZE + 2*PADDING, reveal_ships=False)

    # Draw UI
    draw_ui()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
