import argparse
import contextlib
import io
import random
import time

import numpy as np

import engine
import random_moves
from gameboard import GameBoard

MAX_TURNS = 500

# Plays the engine (as the player side) against random moves (as the AI side)
# Returns True if the engine wins, False if random moves wins, None if the turn limit is hit
def run_game(engine_first: bool) -> tuple[bool | None, int]:
    game: GameBoard = GameBoard()
    turns = 0
    engine_turn = engine_first
    while not game.is_won() and turns < MAX_TURNS:
        if engine_turn:
            engine.deploy(game, True)
            engine.attack(game, True)
            engine.fortify(game, True)
        else:
            random_moves.deploy(game, False)
            random_moves.attack(game, False)
            random_moves.fortify(game, False)
        assert (game.armies >= 1).all(), "a territory was left with no troops"
        engine_turn = not engine_turn
        turns += 1
    return game.winner(), turns

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Play the engine against random moves")
    parser.add_argument("--games", type = int, default = 100)
    parser.add_argument("--seed", type = int, default = None)
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)
        np.random.seed(args.seed)

    results = {True: 0, False: 0, None: 0}
    total_turns = 0
    start_time = time.time()
    for i in range(args.games):
        # hide the move-by-move output
        with contextlib.redirect_stdout(io.StringIO()):
            winner, turns = run_game(i % 2 == 0)
        results[winner] += 1
        total_turns += turns

    print(f"Engine won {results[True]}, random won {results[False]}, unfinished {results[None]} out of {args.games} games")
    print(f"Average {total_turns / args.games:.1f} turns, {(time.time() - start_time) / args.games:.2f}s per game")
