class PvPHandler:
    """
    Pure controller for PvP mode.
    Main.py supplies Player objects & Boards.
    This file does NOT import anything from the project.
    """

    def __init__(self, player1, player2):
        self.players = [player1, player2]
        self.current_turn = 0  # index of current player
        self.game_over = False
        self.winner = None

    def get_current_player(self):
        return self.players[self.current_turn]

    def get_opponent(self):
        return self.players[1 - self.current_turn]

    def fire(self, row, col):
        """Current player fires at the opponent."""
        attacker = self.get_current_player()
        defender = self.get_opponent()

        # defender.board MUST implement take_shot()
        result = defender.board.take_shot(row, col)

        # Check for loss (Board must track remaining ships)
        if defender.board.all_ships_sunk():
            self.game_over = True
            self.winner = attacker
            return result, True  # hit/miss, game_over

        # Switch turns only on valid result
        self.current_turn = 1 - self.current_turn
        return result, False  # hit/miss, not game over
