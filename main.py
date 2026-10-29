import argparse
import random

import numpy as np

import engine
import gameboard
from gameboard import GameBoard
import player
import random_moves

# Asks for any player counts not given on the command line, until the mix is valid
def choose_players(humans: int | None, ais: int | None) -> tuple[int, int]:
    while True:
        while humans is None:
            humans = player.ask_int(f"How many human players? (0 to {gameboard.MAX_PLAYERS}) ", 0, gameboard.MAX_PLAYERS)
        while ais is None:
            ais = player.ask_int(f"How many AI players? (0 to {gameboard.MAX_PLAYERS - humans}) ", 0, gameboard.MAX_PLAYERS)

        problem = gameboard.check_player_counts(humans, ais)
        if problem is None:
            return humans, ais
        print(problem)
        humans, ais = None, None

def play(humans: int, ais: int, easy: bool) -> None:
    game: GameBoard = GameBoard(humans + ais)
    ai = random_moves if easy else engine
    print("Players: " + ", ".join(gameboard.player_name(p, humans) for p in range(game.num_players)))

    current: int = 0
    turns: int = 0
    try:
        while not game.is_won():
            if humans == 0 and turns >= gameboard.AI_ONLY_TURN_LIMIT:
                print(f"\nNo winner after {turns} turns. Final standings:")
                for p, territories, troops in game.standings():
                    print(f"{gameboard.player_name(p, humans)}: {territories} territories, {troops} troops")
                return

            print(f"\nIt is now {gameboard.player_name(current, humans)}'s turn")
            controller = player if current < humans else ai
            alive_before: list[int] = game.alive_players()

            controller.deploy(game, current)
            controller.attack(game, current)

            # human players are told about eliminations as they happen
            if controller is ai:
                for p in alive_before:
                    if not game.is_alive(p):
                        print(f"{gameboard.player_name(p, humans)} has been eliminated!")

            if game.is_won():
                break
            controller.fortify(game, current)

            current = game.next_player(current)
            turns += 1
    except (EOFError, KeyboardInterrupt):
        print("\nGame ended.")
        return

    print(f"{gameboard.player_name(game.winner(), humans)} has won the game!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Play deterministic Risk with up to 6 human and AI players")
    parser.add_argument("--humans", type = int, default = None, help = "number of human players (asked at the start if not given)")
    parser.add_argument("--ais", type = int, default = None, help = "number of AI players (asked at the start if not given)")
    parser.add_argument("--gui", action = "store_true", help = "play on the clickable map instead of the terminal")
    parser.add_argument("--easy", action = "store_true", help = "AI players use random moves instead of the engine")
    parser.add_argument("--seed", type = int, default = None, help = "seed for the starting board and random moves")
    args = parser.parse_args()

    if args.humans is not None and args.ais is not None:
        problem = gameboard.check_player_counts(args.humans, args.ais)
        if problem:
            parser.error(problem)

    if args.seed is not None:
        random.seed(args.seed)
        np.random.seed(args.seed)

    if args.gui:
        # the GUI's start screen picks the players, starting from these numbers
        from interface import gui
        gui.run(args.easy, args.humans, args.ais)
    else:
        try:
            humans, ais = choose_players(args.humans, args.ais)
        except (EOFError, KeyboardInterrupt):
            print()
        else:
            play(humans, ais, args.easy)
