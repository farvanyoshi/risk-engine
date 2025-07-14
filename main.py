from gameboard import GameBoard

game = GameBoard()
while not game.is_won():
    game.initiate_turn()