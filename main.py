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
        # print(f"{"player" if player else "AI"}'s turn" )
        # print(territory.territory_names[game.owners])
        # print(territory.territory_names[~game.owners])
        engine.deploy(game, player)
        engine.attack(game, player)
        engine.fortify(game, player)

        # print("ai's turn")
        # print(territory.territory_names[game.owners])
        # print(territory.territory_names[~game.owners])
        random_moves.deploy(game, not player)
        random_moves.attack(game, not player)
        random_moves.fortify(game, not player)
        count += 1
        player = not player

    print(count)
    return not player

print(run_game(True))

# i = 0
# player_wins = 0
# # player = True
# while i < 10000:
#     player_wins += run_game(i % 2 == 0)
#     i += 1
#     # player = not player

# print(player_wins, "out of", i)