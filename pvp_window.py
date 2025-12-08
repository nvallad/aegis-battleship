# pvp_window.py
import pygame
from pvp_shared import place_ship_shared, fire_shared

ROWS, COLS = 10, 10
CELL_SIZE = 40
PADDING = 20
SCREEN_WIDTH = 2 * (COLS * CELL_SIZE) + 3 * PADDING
SCREEN_HEIGHT = ROWS * CELL_SIZE + 2 * PADDING + 40

BLACK = (20, 20, 20)
WHITE = (240, 240, 240)
GRAY = (120, 120, 120)
RED = (220, 40, 40)
BLUE = (30, 144, 255)
GREEN = (60, 200, 80)
PREVIEW_ALPHA = 140

SHIP_DEFS = [
    ("Carrier", 5),
    ("Battleship", 4),
    ("Cruiser", 3),
    ("Submarine", 3),
    ("Destroyer", 2),
]

POPUP_WIDTH = 300
POPUP_HEIGHT = 150
BUTTON_WIDTH = 120
BUTTON_HEIGHT = 40
BUTTON_SPACING = 20

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


def _make_ships():
    return [{"name": name, "size": size} for name, size in SHIP_DEFS]


def run_pvp(player_number=None, shared_state=None):
    if shared_state is None:
        # Fallback: single-window standalone mode (not used in multi-window PvP)
        from pvp_shared import init_shared_state
        shared_state = init_shared_state()

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    title = "Local PvP — Place Ships"
    if player_number is not None:
        title = f"Local PvP — Player {player_number}"
    pygame.display.set_caption(title)
    font = pygame.font.SysFont(None, 24)
    clock = pygame.time.Clock()

    # State local to this window
    player_idx = (player_number - 1) if player_number else 0
    opponent_idx = 1 - player_idx
    placing = True
    current_ship_index = 0
    orientation = "H"
    highlight = None
    game_won = False
    winner = None

    message = f"Player {player_number or 1}: place your ships"
    message_timer = 0

    def board_offset(left=True):
        if left:
            return PADDING
        return COLS * CELL_SIZE + 2 * PADDING

    def get_tile(pos, offset_x):
        x, y = pos
        col = (x - offset_x) // CELL_SIZE
        row = (y - PADDING) // CELL_SIZE
        return row, col

    def draw_board(board_grid, offset_x, reveal_ships=False):
        for r in range(ROWS):
            for c in range(COLS):
                rect = pygame.Rect(offset_x + c * CELL_SIZE, PADDING + r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                cell = board_grid[r][c]
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
                if event.key == pygame.K_r and not game_won:
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
                
                if placing:
                    # Ship placement phase: only allow this player to place on left board
                    offset = board_offset(left=True)
                    row, col = get_tile(event.pos, offset)
                    if 0 <= row < ROWS and 0 <= col < COLS:
                        ship_def = SHIP_DEFS[current_ship_index]
                        success = place_ship_shared(shared_state, player_idx, ship_def[0], ship_def[1], (row, col), orientation)
                        if success:
                            current_ship_index += 1
                            if current_ship_index >= len(SHIP_DEFS):
                                # This player is done placing
                                shared_state[f'player{player_idx + 1}_placement_done'] = True
                                placing = False
                                message = f"Player {player_number or 1} ready. Waiting for opponent..."
                                message_timer = pygame.time.get_ticks()
                else:
                    # Game phase: only allow this player to fire when it's their turn and both placed
                    if not (shared_state['player1_placement_done'] and shared_state['player2_placement_done']):
                        continue  # Not ready yet
                    if shared_state['current_turn'] != player_idx:
                        continue
                    
                    offset = board_offset(left=False)
                    row, col = get_tile(event.pos, offset)
                    if 0 <= row < ROWS and 0 <= col < COLS:
                        result, _ = fire_shared(shared_state, player_idx, row, col)
                        
                        # Check if game is over
                        if shared_state['game_over']:
                            game_won = True
                            winner = shared_state['winner']
                        # Interpret result for message display
                        elif result == "miss":
                            message = f"Missed at ({row},{col}). {shared_state[f'player{opponent_idx+1}_name']}'s turn."
                            shared_state['current_turn'] = opponent_idx
                        elif result == "hit":
                            message = f"Hit at ({row},{col})! {shared_state[f'player{opponent_idx+1}_name']}'s turn."
                        elif isinstance(result, tuple) and result[0] == "sunk":
                            message = f"Sunk {result[1]}! {shared_state[f'player{opponent_idx+1}_name']}'s turn."
                        else:
                            message = f"Result: {result}"
                        message_timer = pygame.time.get_ticks()

        # Ship preview while placing
        if placing:
            pr, pc = get_tile(mouse_pos, board_offset(left=True))
            ship_def = SHIP_DEFS[current_ship_index]
            coords = []
            valid = True
            for i in range(ship_def[1]):
                rr = pr + (i if orientation == "V" else 0)
                cc = pc + (i if orientation == "H" else 0)
                coords.append((rr, cc))
                if rr < 0 or cc < 0 or rr >= ROWS or cc >= COLS:
                    valid = False
                else:
                    # Check collision in shared state (only if in bounds)
                    own_board = shared_state[f'player{player_idx + 1}_board_grid']
                    if own_board[rr][cc] != "~":
                        valid = False
            highlight = {"coords": coords, "valid": valid}

        # Get board grids and determine view
        own_board = shared_state[f'player{player_idx + 1}_board_grid']
        opponent_board = shared_state[f'player{opponent_idx + 1}_board_grid']

        # Check if both players are done placing
        if not placing and shared_state['player1_placement_done'] and shared_state['player2_placement_done']:
            placing = False  # Ensure we stay in game phase
        elif not placing and (not shared_state['player1_placement_done'] or not shared_state['player2_placement_done']):
            # One player is done, but the other isn't — stay in waiting mode
            pass

        draw_board(own_board, board_offset(left=True), reveal_ships=True)
        draw_board(opponent_board, board_offset(left=False), reveal_ships=False)

        # Draw preview squares
        if placing and highlight:
            s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            color = (GREEN[0], GREEN[1], GREEN[2], PREVIEW_ALPHA) if highlight["valid"] else (255, 80, 80, PREVIEW_ALPHA)
            s.fill(color)
            for (r, c) in highlight["coords"]:
                if 0 <= r < ROWS and 0 <= c < COLS:
                    rect = pygame.Rect(PADDING + c * CELL_SIZE, PADDING + r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    screen.blit(s, (rect.x, rect.y))

        # UI text
        if placing:
            txt = font.render(message, True, WHITE)
            screen.blit(txt, (PADDING, SCREEN_HEIGHT - 30))
        else:
            # Check if both are ready before showing game phase
            if shared_state['player1_placement_done'] and shared_state['player2_placement_done']:
                if not game_won:
                    current_player_num = shared_state['current_turn'] + 1
                    turn_txt = font.render(f"Turn: Player {current_player_num}", True, WHITE)
                    screen.blit(turn_txt, (PADDING, SCREEN_HEIGHT - 30))
                    if message:
                        msg_surf = font.render(message, True, WHITE)
                        screen.blit(msg_surf, (PADDING + 200, SCREEN_HEIGHT - 30))
            else:
                # Still waiting for opponent
                txt = font.render(message, True, WHITE)
                screen.blit(txt, (PADDING, SCREEN_HEIGHT - 30))

        # Draw popup if game is won
        if game_won:
            button_rects = {}
            draw_popup(screen, f"{winner} WINS!", button_rects)

        pygame.display.flip()
        clock.tick(60)
