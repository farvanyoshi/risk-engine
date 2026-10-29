import argparse
import contextlib
import io
import random
import time

import numpy as np

import engine
import gameboard
import random_moves
from gameboard import GameBoard

# turns are counted per player, so bigger games get more of them
MAX_ROUNDS = 250

# Plays the engine (player 0) against random moves (every other player)
# Returns the winner's number (or None if the turn limit is hit) and the number of turns played
def run_game(num_players: int, first_player: int) -> tuple[int | None, int]:
    game: GameBoard = GameBoard(num_players)
    turns = 0
    current = first_player
    while not game.is_won() and turns < MAX_ROUNDS * num_players:
        ai = engine if current == 0 else random_moves
        ai.deploy(game, current)
        ai.attack(game, current)
        if not game.is_won():
            ai.fortify(game, current)
        assert (game.armies >= 1).all(), "a territory was left with no troops"
        current = game.next_player(current)
        turns += 1
    return game.winner(), turns

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Play the engine against random moves")
    parser.add_argument("--games", type = int, default = 100)
    parser.add_argument("--players", type = int, default = 2, help = f"total players, {gameboard.MIN_PLAYERS} to {gameboard.MAX_PLAYERS} (the engine is one of them)")
    parser.add_argument("--seed", type = int, default = None)
    args = parser.parse_args()

    if not gameboard.MIN_PLAYERS <= args.players <= gameboard.MAX_PLAYERS:
        parser.error(f"--players must be between {gameboard.MIN_PLAYERS} and {gameboard.MAX_PLAYERS}")

    if args.seed is not None:
        random.seed(args.seed)
        np.random.seed(args.seed)

    engine_wins = random_wins = unfinished = 0
    total_turns = 0
    start_time = time.time()
    for i in range(args.games):
        # hide the move-by-move output, and rotate who goes first
        with contextlib.redirect_stdout(io.StringIO()):
            winner, turns = run_game(args.players, i % args.players)
        if winner is None:
            unfinished += 1
        elif winner == 0:
            engine_wins += 1
        else:
            random_wins += 1
        total_turns += turns

    print(f"{args.players} players: engine won {engine_wins}, random moves won {random_wins}, unfinished {unfinished} out of {args.games} games")
    print(f"(winning by chance would be about {args.games / args.players:.0f})")
    print(f"Average {total_turns / args.games:.1f} turns, {(time.time() - start_time) / args.games:.2f}s per game")
