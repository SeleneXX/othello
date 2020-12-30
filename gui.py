import pygame, board

Board = board.Board()
game = board.Game(Board)
while True:
    if game.runGame() == False:
        break