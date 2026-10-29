import argparse
import random

import numpy as np

import engine
from gameboard import GameBoard
import player
import random_moves

def play(easy: bool) -> None:
    game: GameBoard = GameBoard()
    ai = random_moves if easy else engine

    try:
        while not game.is_won():
            print("\nIt is now the player's turn")
            player.deploy(game, True)
            player.attack(game, True)
            if game.is_won():
                break
            player.fortify(game, True)

            print("\nIt is now the AI's turn")
            ai.deploy(game, False)
            ai.attack(game, False)
            if game.is_won():
                break
            ai.fortify(game, False)
    except (EOFError, KeyboardInterrupt):
        print("\nGame ended.")
        return

    print("The player has won the game!" if game.winner() else "The AI has won the game!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Play deterministic Risk against the computer")
    parser.add_argument("--gui", action = "store_true", help = "play on the clickable map instead of the terminal")
    parser.add_argument("--easy", action = "store_true", help = "play against random moves instead of the engine")
    parser.add_argument("--seed", type = int, default = None, help = "seed for the starting board and random moves")
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)
        np.random.seed(args.seed)

    if args.gui:
        from interface import gui
        gui.run(args.easy)
    else:
        play(args.easy)
