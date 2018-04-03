import sys, os, random, pygame
sys.path.append(os.path.join("objects"))
import SudokuSquare
from utils import *
from GameResources import *


def play(values, result, history):
    assignments = reconstruct(result, history)
    pygame.init()

    size = width, height = 700, 700
    screen = pygame.display.set_mode(size)

    background_image = pygame.image.load("./images/sudoku-board-bare.jpg").convert()

    clock = pygame.time.Clock()

    while True:
        pygame.event.pump()
        theSquares = []
        initXLoc = 0
        initYLoc = 0
        startX, startY, editable, number = 0, 0, "N", 0
        for y in range(9):
            for x in range(9):
                if x in (0, 1, 2):  startX = (x * 57) + 38
                if x in (3, 4, 5):  startX = (x * 57) + 99
                if x in (6, 7, 8):  startX = (x * 57) + 159

                if y in (0, 1, 2):  startY = (y * 57) + 35
                if y in (3, 4, 5):  startY = (y * 57) + 100
                if y in (6, 7, 8):  startY = (y * 57) + 165
                string_number = values[rows[y] + cols[x]]
                if len(string_number) > 1 or string_number == '' or string_number == '.':
                    number = None
                else:
                    number = int(string_number)
                theSquares.append(SudokuSquare.SudokuSquare(number, startX, startY, editable, x, y))

        screen.blit(background_image, (0, 0))
        for num in theSquares:
            num.draw()

        pygame.display.flip()
        pygame.display.update()
        clock.tick(5)

        if len(assignments) == 0:
            break
        box, value = assignments.pop()
        values[box] = value

    # leave game showing until closed by user
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
