from gameboard import GameBoard

global game

if __name__ == '__main__':
    game = GameBoard()
    while not game.won():
        game.initiate_turn()