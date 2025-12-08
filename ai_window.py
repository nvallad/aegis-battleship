# ai_window.py
import pygame
from board import Board
from ship import Ship
from player import Player
from AI import AI
from game_logic import GameLogic

ROWS, COLS = 10, 10
CELL_SIZE = 40
PADDING = 20
SCREEN_WIDTH = 2 * (COLS*CELL_SIZE) + 3*PADDING
SCREEN_HEIGHT = ROWS*CELL_SIZE + 2*PADDING + 40

BLACK = (20, 20, 20)
WHITE = (240, 240, 240)
GRAY = (120, 120, 120)
RED = (220, 40, 40)
BLUE = (30, 144, 255)
GREEN = (60, 200, 80)
YELLOW = (230, 200, 40)
PREVIEW_ALPHA = 140

POPUP_WIDTH = 300
POPUP_HEIGHT = 150
BUTTON_WIDTH = 120
BUTTON_HEIGHT = 40
BUTTON_SPACING = 20

ships_to_place = [
    Ship("Carrier", 5),
    Ship("Battleship", 4),
    Ship("Cruiser", 3),
    Ship("Submarine", 3),
    Ship("Destroyer", 2)
]

def draw_popup(screen, message, button_rects):
    """Draw a popup dialog with message and buttons."""
    popup_x = (SCREEN_WIDTH - POPUP_WIDTH) // 2
    popup_y = (SCREEN_HEIGHT - POPUP_HEIGHT) // 2
    
    # Draw semi-transparent overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))
    
    # Draw popup background
    popup_rect = pygame.Rect(popup_x, popup_y, POPUP_WIDTH, POPUP_HEIGHT)
    pygame.draw.rect(screen, WHITE, popup_rect)
    pygame.draw.rect(screen, GRAY, popup_rect, 2)
    
    # Draw message
    font_large = pygame.font.SysFont(None, 28)
    msg_surf = font_large.render(message, True, BLACK)
    msg_rect = msg_surf.get_rect(center=(SCREEN_WIDTH // 2, popup_y + 40))
    screen.blit(msg_surf, msg_rect)
    
    # Draw buttons
    font_button = pygame.font.SysFont(None, 24)
    for i, (label, color) in enumerate([("Play Again", GREEN), ("Quit", RED)]):
        btn_x = popup_x + 35 + i * (BUTTON_WIDTH + BUTTON_SPACING)
        btn_y = popup_y + POPUP_HEIGHT - 60
        btn_rect = pygame.Rect(btn_x, btn_y, BUTTON_WIDTH, BUTTON_HEIGHT)
        button_rects[label] = btn_rect
        
        pygame.draw.rect(screen, color, btn_rect)
        pygame.draw.rect(screen, BLACK, btn_rect, 2)
        
        btn_surf = font_button.render(label, True, BLACK)
        btn_text_rect = btn_surf.get_rect(center=btn_rect.center)
        screen.blit(btn_surf, btn_text_rect)

def run_ai():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Battleship vs AI")
    font = pygame.font.SysFont(None, 24)
    clock = pygame.time.Clock()

    # Boards
    player_board = Board(ROWS, COLS)
    player = Player("Player", player_board)

    ai_board = Board(ROWS, COLS)
    ai_player = Player("CPU", ai_board)
    ai_player.is_ai = True
    ai_player.ai = AI(ai_player, difficulty="easy")

    game = GameLogic(player, ai_player)
    game.auto_place_ships_if_ai()

    placing_ships = True
    current_ship_index = 0
    orientation = "H"
    highlight = None
    game_won = False
    winner = None

    def get_tile(pos, offset_x):
        x, y = pos
        col = (x - offset_x) // CELL_SIZE
        row = (y - PADDING) // CELL_SIZE
        return row, col

    def draw_board(board, offset_x, reveal_ships=True):
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

    running = True
    while running:
        screen.fill(BLACK)
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if placing_ships and event.key == pygame.K_r:
                    orientation = "V" if orientation == "H" else "H"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Handle popup clicks
                if game_won:
                    button_rects = {}
                    popup_x = (SCREEN_WIDTH - POPUP_WIDTH) // 2
                    popup_y = (SCREEN_HEIGHT - POPUP_HEIGHT) // 2
                    
                    for i, label in enumerate(["Play Again", "Quit"]):
                        btn_x = popup_x + 35 + i * (BUTTON_WIDTH + BUTTON_SPACING)
                        btn_y = popup_y + POPUP_HEIGHT - 60
                        btn_rect = pygame.Rect(btn_x, btn_y, BUTTON_WIDTH, BUTTON_HEIGHT)
                        button_rects[label] = btn_rect
                    
                    if button_rects.get("Play Again", pygame.Rect(0, 0, 0, 0)).collidepoint(event.pos):
                        running = False  # Exit game loop to restart
                    elif button_rects.get("Quit", pygame.Rect(0, 0, 0, 0)).collidepoint(event.pos):
                        pygame.quit()
                        import sys
                        sys.exit()
                    continue
                
                if placing_ships:
                    row, col = get_tile(event.pos, PADDING)
                    if 0 <= row < ROWS and 0 <= col < COLS:
                        ship = ships_to_place[current_ship_index]
                        success = player.add_ship(ship, (row, col), orientation)
                        if success:
                            current_ship_index += 1
                            if current_ship_index >= len(ships_to_place):
                                placing_ships = False
                else:
                    row, col = get_tile(event.pos, COLS*CELL_SIZE + 2*PADDING)
                    if 0 <= row < ROWS and 0 <= col < COLS:
                        result = game.fire(row, col)
                        print("FIRE RESULT:", result)
                        
                        # Check if game is over
                        if game.is_game_over():
                            game_won = True
                            winner = game.get_current_player().name
                        else:
                            if game.get_current_player().is_ai:
                                ai_result = game.ai_take_turn()
                                print("AI RESULT:", ai_result)
                                if game.is_game_over():
                                    game_won = True
                                    winner = game.get_current_player().name

        # Draw ship placement preview
        if placing_ships:
            pr, pc = get_tile(mouse_pos, PADDING)
            ship = ships_to_place[current_ship_index]
            coords = []
            valid = True
            for i in range(ship.size):
                rr = pr + (i if orientation == "V" else 0)
                cc = pc + (i if orientation == "H" else 0)
                coords.append((rr, cc))
                if rr < 0 or cc < 0 or rr >= ROWS or cc >= COLS:
                    valid = False
                else:
                    # Check collision with existing ships
                    if player.board.grid[rr][cc] != "~":
                        valid = False
            highlight = {"coords": coords, "valid": valid}

        draw_board(player.board, PADDING, reveal_ships=True)
        draw_board(ai_player.board, COLS*CELL_SIZE + 2*PADDING, reveal_ships=False)
        
        # Draw preview squares during ship placement
        if placing_ships and highlight:
            s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            color = (GREEN[0], GREEN[1], GREEN[2], PREVIEW_ALPHA) if highlight["valid"] else (255, 80, 80, PREVIEW_ALPHA)
            s.fill(color)
            for (r, c) in highlight["coords"]:
                if 0 <= r < ROWS and 0 <= c < COLS:
                    rect = pygame.Rect(PADDING + c * CELL_SIZE, PADDING + r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    screen.blit(s, (rect.x, rect.y))
        
        # Draw popup if game is won
        if game_won:
            button_rects = {}
            draw_popup(screen, f"{winner} WINS!", button_rects)
        
        pygame.display.flip()
        clock.tick(60)
