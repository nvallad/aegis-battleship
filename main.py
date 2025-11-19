# Title: Main Battleship Test
# Author: Nathan Vallad
# Date: 11/17/2025
# Purpose: Test the Ship and Board classes using Pygame. Allows placing ships on the board
# and firing shots by clicking cells. Displays hits, misses, and sunk ships visually.

import pygame
from board import Board
from ship import Ship

# Constants
CELL_SIZE = 40
ROWS, COLS = 10, 10
SCREEN_WIDTH = COLS * CELL_SIZE
SCREEN_HEIGHT = ROWS * CELL_SIZE

# Colors
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Battleship Test")
clock = pygame.time.Clock()

# Create Board and Ships
board = Board(ROWS, COLS)
destroyer = Ship("Destroyer", 3)
board.place_ship(destroyer, (2, 2), "H")

# Draw Board Function
def draw_board(board):
    for r in range(board.rows):
        for c in range(board.cols):
            rect = pygame.Rect(c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            cell = board.grid[r][c]
            
            if cell == "~":
                color = BLUE
            elif cell == "S":
                color = GRAY  # You can hide ships by using BLUE here
            elif cell == "X":
                color = RED
            elif cell == "O":
                color = WHITE
            
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)  # grid lines

# Main Loop
running = True
while running:
    screen.fill(BLUE)
    draw_board(board)
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            row = mouse_y // CELL_SIZE
            col = mouse_x // CELL_SIZE

            result = board.take_shot((row, col))
            print(f"Shot at {(row, col)}: {result}")
            if board.all_ships_sunk():
                print("All ships sunk! You win!")
                running = False

    clock.tick(60)

pygame.quit()
