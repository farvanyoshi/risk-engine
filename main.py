from gameboard import GameBoard
import player

global game

if __name__ == '__main__':
    game = GameBoard()
    while not game.is_won():
        game.initiate_turn()