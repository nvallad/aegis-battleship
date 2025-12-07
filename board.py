# Title: Board Class
# Author: Nathan Vallad
# Date: 11/17/2025
# Purpose: Define the Board class for the Battleship game. Handles ship placement,
# shot tracking, checking hits/misses/sunk ships, and determining if all ships are sunk.

class Board:
    def __init__(self, rows=10, cols=10):
        self.rows = rows
        self.cols = cols
        self.ships = []
        self.shots_taken = set()  # Tracks coordinates already shot

        self.grid = [["~" for _ in range(cols)] for _ in range(rows)]

    def in_bounds(self, r, c) -> bool:
        return 0 <= r < self.rows and 0 <= c < self.cols

    def can_place(self, ship, start, direction) -> bool:
        r, c = start

        # Generate position coordinates
        for i in range(ship.size):
            nr = r + (i if direction == 'V' else 0)
            nc = c + (i if direction == 'H' else 0)

            if not self.in_bounds(nr, nc):
                return False

            for s in self.ships:
                if (nr, nc) in s.positions:
                    return False

        return True

    def place_ship(self, ship, start, direction) -> bool:
        if not self.can_place(ship, start, direction):
            return False

        ship.place(start, direction)
        self.ships.append(ship)

        # Update grid 
        for (r, c) in ship.positions:
            self.grid[r][c] = "S"

        return True

    def take_shot(self, row, col):
        """
        Process an attack at (row, col).
        Returns:
            "hit", "miss", or ("sunk", ship)
        """
        cell = self.grid[row][col]

        # Already hit
        if cell in ["X", "O"]:
            return "miss"

        for ship in self.ships:
            if (row, col) in ship.positions:
                ship.register_hit((row, col))
                self.grid[row][col] = "X"
                if ship.is_sunk():
                    return ("sunk", ship)
                return "hit"

        self.grid[row][col] = "O"
        return "miss"

    def all_ships_sunk(self) -> bool:
        return all(ship.is_sunk() for ship in self.ships)