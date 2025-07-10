from gameboard import GameBoard

if __name__ == '__main__':
    game = GameBoard()
    while not game.won():
        game.move()