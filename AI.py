# Title: AI Class
# Author: Nathan Vallad
# Date: 11/19/2025
# Purpose: Provide decision-making logic for AI-controlled Battleship players.
# Handles selecting moves, placing ships, and maintaining targeting memory while
# delegating all game-rule enforcement to the Player and Board classes.

from player import Player
from board import Board
from ship import Ship
import random


class AI:
    def __init__(self, player: Player, difficulty: str = "easy"):
        
        # AI brain that controls a Player object.
        # Difficulty options: 'easy', 'medium', 'hard'
        
        self.player = player
        self.difficulty = difficulty

        # Memory for targeting behavior
        self.previous_shots = set()
        self.hit_stack = []   # for medium/hard targeting behavior

    # SHIP PLACEMENT
    def place_ships(self, ship_list):
        
        # Given a list of Ship objects, place them on the Player's board.
        # This is where the AI decides *where* to put each ship.
        
        for ship in ship_list:
            placed = False
            while not placed:
                # EASY: random placement (can be improved later)
                row = random.randint(0, self.player.board.rows - 1)
                col = random.randint(0, self.player.board.cols - 1)
                direction = random.choice(["H", "V"])

                placed = self.player.add_ship(ship, (row, col), direction)
                
    # ATTACK DECISION
    def choose_shot(self, opponent_board: Board) -> tuple:
        # Decide where to fire based on difficulty level.
        # Returns (row, col).
        if self.difficulty == "easy":
            return self._choose_shot_easy(opponent_board)
        elif self.difficulty == "medium":
            return self._choose_shot_medium(opponent_board)
        else:  # hard
            return self._choose_shot_hard(opponent_board)

    # EASY MODE (random)
    def _choose_shot_easy(self, opponent_board):
        # Shoot randomly at an unshot tile.
        rows = opponent_board.rows
        cols = opponent_board.cols

        choice = None

        while choice is None or choice in self.previous_shots:
            choice = (random.randint(0, rows - 1),
                      random.randint(0, cols - 1))

        self.previous_shots.add(choice)
        return choice

    # MEDIUM MODE (hunt + target)
    def _choose_shot_medium(self, opponent_board):
        # Hunt mode: random until a hit.
        # Target mode: check tiles around hits.
        
        # TODO: Implement targeting behavior
        return self._choose_shot_easy(opponent_board)

    # HARD MODE (advanced patterning or probability map)
    def _choose_shot_hard(self, opponent_board):
        # Use a smarter approach: parity, probability density,
        # or pattern scanning (to be implemented).
        
        # TODO: Implement probability targeting
        return self._choose_shot_easy(opponent_board)

    # FULL TURN ACTION
    def take_turn(self, opponent_player: Player):
        # AI selects a shot, then uses Player.fire_at()
        # to actually take the shot.
        coord = self.choose_shot(opponent_player.board)
        result = self.player.fire_at(opponent_player.board, coord)
        return coord, result
