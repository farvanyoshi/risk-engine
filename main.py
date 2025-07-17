from gameboard import GameBoard
import risk-interface/interface

game = GameBoard()
while not game.is_won():
    game.initiate_turn()