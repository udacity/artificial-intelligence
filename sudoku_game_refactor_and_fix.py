import sys
import os
import pygame

# Ensure the correct path is added for imports
sys.path.append(os.path.join("objects"))

# Importing the necessary modules
from SudokuSquare import SudokuSquare
from utils import reconstruct
from GameResources import rows, cols

def play(values, result, history):
    """Main function to play the Sudoku game."""
    # Reconstruct the Sudoku assignments from the result and history
    assignments = reconstruct(result, history)
    pygame.init()

    # Set up the screen size and create the display
    size = width, height = 700, 700
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("Sudoku Game")

    # Load the background image
    background_image = pygame.image.load("./images/sudoku-board-bare.jpg").convert()

    clock = pygame.time.Clock()

    while True:
        pygame.event.pump()
        theSquares = []

        # Calculate positions and initialize Sudoku squares
        for y in range(9):
            for x in range(9):
                startX = (x // 3 * 57) + 38 + (x % 3 * 61)
                startY = (y // 3 * 57) + 35 + (y % 3 * 65)
                
                string_number = values[rows[y] + cols[x]]
                number = int(string_number) if string_number.isdigit() else None
                theSquares.append(SudokuSquare(number, startX, startY, editable="N", x=x, y=y))

        # Draw the background and squares on the screen
        screen.blit(background_image, (0, 0))
        for square in theSquares:
            square.draw(screen)

        pygame.display.flip()
        clock.tick(5)

        if not assignments:
            break
        box, value = assignments.pop()
        values[box] = value

    # Keep the game window open until the user closes it
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

if __name__ == "__main__":
    # Example values for testing (replace with actual values as needed)
    values = {}
    result = {}
    history = []
    play(values, result, history)
