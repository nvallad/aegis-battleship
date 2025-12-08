# Title: Game Logic
# Author: Nathan Vallad
# Date: 12/01/2025
# Purpose: Handle all Battleship gameplay rules such as turn 
# management, firing, hit/miss/sunk detection, and win checks. 
# Works with Player and AI objects while keeping graphics and 
# user input separated in main.py.

from ship import Ship

DEFAULT_SHIPS = [
    ("Carrier", 5),
    ("Battleship", 4),
    ("Cruiser", 3),
    ("Submarine", 3),
    ("Destroyer", 2)
]

class GameLogic:
    def __init__(self, player1, player2):
        """
        GameLogic manages only gameplay rules. It does NOT use
        pygame or any rendering code.
        """
        self.players = [player1, player2]
        self.current_turn = 0  # 0 = player1, 1 = player2

    # Access the active player
    def get_current_player(self):
        return self.players[self.current_turn]

    # Access the opponent player
    def get_opponent(self):
        return self.players[(self.current_turn + 1) % 2]

    # Automatically place ships for AI players
    def auto_place_ships_if_ai(self):
        """
        AI automatically places ships at the start of the game.
        Human players place ships in main.py (pygame).
        """
        for player in self.players:
            if hasattr(player, "is_ai") and player.is_ai:
                # Convert DEFAULT_SHIPS tuples to Ship objects
                ships = [Ship(name, size) for name, size in DEFAULT_SHIPS]
                player.ai.place_ships(ships)

    # Handle a player firing at a coordinate
    def fire(self, row, col):
        """
        Called by main.py when a player attempts to fire.
        Returns:
            ("hit", ship)
            ("miss", None)
            ("sunk", ship)
            ("win", None)
        """
        attacker = self.get_current_player()
        defender = self.get_opponent()

        result = defender.board.take_shot(row, col)

        # Check win condition
        if self.is_game_over():
            return ("win", None)

        # Switch turn if miss
        if result == "miss":
            self.end_turn()
        
        elif result == "hit":
            self.end_turn()
            
        else:  # sunk
            self.end_turn()

        return result

    # Execute the AI's move (if the active player is an AI)
    def ai_take_turn(self):
        """
        Returns same result types as fire(): 
        ("hit", ship), ("miss", None), ("sunk", ship), ("win", None)
        """
        current = self.get_current_player()

        # Not an AI
        if not hasattr(current, "is_ai") or not current.is_ai:
            return None

        row, col = current.ai.choose_shot(self.get_opponent().board)
        return self.fire(row, col)

    # Switch turn to the other player
    def end_turn(self):
        self.current_turn = (self.current_turn + 1) % 2

    # Check if the game is over (opponent has no ships left)
    def is_game_over(self):
        opponent = self.get_opponent()
        return opponent.board.all_ships_sunk()
