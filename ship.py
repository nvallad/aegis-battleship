# Title: Ship Class
# Author: Nathan Vallad
# Date: 11/17/2025
# Purpose: Define the Ship class for the Battleship game. Handles ship name, size, position,
# hits tracking, placement on the board, registering hits, and checking if the ship is sunk.

class Ship:
    def __init__(self, name: str, size: int):
        self.name = name
        self.size = size
        self.positions = []    # List[(row, col)]
        self.hits = set()      # Set[(row, col)]

    def place(self, start, direction):
        """
        start: (row, col)
        direction: 'H' or 'V'
        """
        r, c = start
        self.positions = []

        for i in range(self.size):
            if direction == 'H':
                self.positions.append((r, c + i))
            elif direction == 'V':
                self.positions.append((r + i, c))
            else:
                raise ValueError("Direction must be 'H' or 'V'")

    def register_hit(self, coord):
        if coord in self.positions:
            self.hits.add(coord)

    def is_sunk(self) -> bool:
        return len(self.hits) == self.size