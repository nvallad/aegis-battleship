# pvp_shared.py
"""
Shared state for multi-window PvP.
Both windows read/write to the same dicts managed by multiprocessing.Manager.
"""

def init_shared_state():
    """
    Returns a dict of shared state that will be managed by multiprocessing.Manager.
    Structure:
    {
        'player1_name': str,
        'player2_name': str,
        'current_turn': int (0 or 1),
        'game_over': bool,
        'winner': str or None,
        'player1_board_grid': list of lists,
        'player2_board_grid': list of lists,
        'player1_ships': list of dicts,
        'player2_ships': list of dicts,
        'player1_placement_done': bool,
        'player2_placement_done': bool,
    }
    """
    return {
        'player1_name': 'Player 1',
        'player2_name': 'Player 2',
        'current_turn': 0,
        'game_over': False,
        'winner': None,
        'player1_board_grid': [["~" for _ in range(10)] for _ in range(10)],
        'player2_board_grid': [["~" for _ in range(10)] for _ in range(10)],
        'player1_ships': [],
        'player2_ships': [],
        'player1_placement_done': False,
        'player2_placement_done': False,
    }


def fire_shared(shared_state, attacker_idx, row, col):
    """
    Simulate a shot in shared state.
    attacker_idx: 0 for Player 1, 1 for Player 2.
    Returns: ("hit" | "miss" | "sunk:<name>", game_over)
    """
    defender_idx = 1 - attacker_idx
    defender_board_key = f'player{defender_idx + 1}_board_grid'
    defender_ships_key = f'player{defender_idx + 1}_ships'
    defender_board = shared_state[defender_board_key]
    defender_ships = shared_state[defender_ships_key]
    
    cell = defender_board[row][col]
    # Already hit
    if cell in ["X", "O"]:
        # Reassign before returning (might be unnecessary but safe)
        shared_state[defender_board_key] = defender_board
        shared_state[defender_ships_key] = defender_ships
        return "miss", False
    # Check for ship hit
    for ship in defender_ships:
        if (row, col) in ship['positions']:
            ship['hits'].append((row, col))
            defender_board[row][col] = "X"
            # End turn on hit
            shared_state['current_turn'] = defender_idx
            if len(ship['hits']) == ship['size']:
                # Sunk
                all_sunk = all(len(s['hits']) == s['size'] for s in defender_ships)
                if all_sunk:
                    shared_state['game_over'] = True
                    shared_state['winner'] = shared_state[f'player{attacker_idx + 1}_name']
                    shared_state[defender_board_key] = defender_board
                    shared_state[defender_ships_key] = defender_ships
                    return (f"sunk", ship['name']), True
                else:
                    shared_state[defender_board_key] = defender_board
                    shared_state[defender_ships_key] = defender_ships
                    return (f"sunk", ship['name']), False
            # Persist changes and return hit
            shared_state[defender_board_key] = defender_board
            shared_state[defender_ships_key] = defender_ships
            return "hit", False
    # Miss
    defender_board[row][col] = "O"
    shared_state['current_turn'] = defender_idx
    shared_state[defender_board_key] = defender_board
    shared_state[defender_ships_key] = defender_ships
    return "miss", False


def place_ship_shared(shared_state, player_idx, ship_name, size, start, direction):
    """
    Place a ship in shared state.
    Returns: True if successful, False if invalid.
    """
    row, col = start
    board_key = f'player{player_idx + 1}_board_grid'
    ships_key = f'player{player_idx + 1}_ships'
    board = shared_state[board_key]
    ships = shared_state[ships_key]
    
    # Generate positions
    positions = []
    for i in range(size):
        r = row + (i if direction == 'V' else 0)
        c = col + (i if direction == 'H' else 0)
        if r >= 10 or c >= 10:
            return False
        positions.append((r, c))
    # Check collision
    for r, c in positions:
        if board[r][c] != "~":
            return False
        for other_ship in ships:
            if (r, c) in other_ship['positions']:
                return False
    # Place ship
    ship = {
        'name': ship_name,
        'size': size,
        'positions': positions,
        'hits': [],
    }
    ships.append(ship)
    for r, c in positions:
        board[r][c] = "S"
    
    # CRITICAL: Reassign to trigger Manager sync (nested list changes don't auto-sync)
    shared_state[board_key] = board
    shared_state[ships_key] = ships
    
    return True
