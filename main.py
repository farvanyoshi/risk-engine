# import engine
from gameboard import GameBoard
import random_moves
import player

game: GameBoard = GameBoard()
while not game.is_won():
    print(f"It is now the {"player" if game.is_player else "AI"}'s turn" )
    if game.is_player:
        player.deploy(game)
        player.attack(game)
        player.fortify(game)
        game.is_player = False
    else:
        random_moves.deploy(game)
        random_moves.attack(game)
        random_moves.fortify(game)
        game.is_player = True

        # engine.deploy_attack(game)
        # engine.fortify(game)