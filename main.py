from gameboard import GameBoard
import engine
import player
import territory

from .interface import gui

game: GameBoard = GameBoard()
while not game.is_won():
    print(f"It is now the {"player" if game.is_player else "AI"}'s turn" )
    if game.is_player == True:
        player.draft(game)
        player.attack(game)
        player.fortify(game)
        game.is_player = False
    elif game.is_player == False:
        engine.draft(game)
        engine.attack(game)
        engine.fortify(game)