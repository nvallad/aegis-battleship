# Title: Player Class
# Author: Nathan Vallad
# Date: 11/19/2025
# Purpose: Represent a Battleship player by managing their own board, ships, and turn actions. 
# Coordinates ship placement and handles firing at opponents while relying on the Board class 
# for hit and placement validation.

from board import Board
from ship import Ship

class Player:
    def __init__(self, name: str, board: Board, is_ai=False):
        # Initialize a player with a name and their board.
        self.name = name
        self.is_ai = is_ai      # Indicates if this player is controlled by AI
        self.board = board
        self.ships = []

    def add_ship(self, ship: Ship, start: tuple, direction: str) -> bool:
        # Request the board to place a ship.
        # Returns True if placement succeeds, False if invalid.
        if self.board.place_ship(ship, start, direction):
            self.ships.append(ship)
            return True
        return False

    def fire_at(self, opponent_board: Board, coord: tuple) -> str:
        # Fire a shot at an opponent’s board.
        # Returns 'hit', 'miss', 'repeat', 'invalid', or 'sunk:<ship name>'.
        return opponent_board.take_shot(coord)

    def has_lost(self) -> bool:
        # Returns True if all the player's ships are sunk.
        return self.board.all_ships_sunk()

    def get_remaining_ships(self):
        # Return a list of ships that have not been sunk yet.
        return [ship for ship in self.ships if not ship.is_sunk()]