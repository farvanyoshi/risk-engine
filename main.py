import engine
from gameboard import GameBoard
import player
import random_moves
import territory

def run_game(first_player):
    game: GameBoard = GameBoard()
    player = first_player
    count = 0
    while not game.is_won():
        print(f"{"player" if player else "AI"}'s turn" )
        print(territory.territory_names[game.owners])
        print(territory.territory_names[~game.owners])
        random_moves.deploy(game, False)
        random_moves.attack(game, False)
        random_moves.fortify(game, False)

        print("ai's turn")
        print(territory.territory_names[game.owners])
        print(territory.territory_names[~game.owners])
        engine.deploy(game, True)
        engine.attack(game, True)
        engine.fortify(game, True)
        count += 1

    print(count)
    return player

run_game(True)

# i = 0
# player_wins = 0
# # player = True
# while i < 10000:
#     player_wins += run_game(i % 2 == 0)
#     i += 1
#     # player = not player

# print(player_wins, "out of", i)