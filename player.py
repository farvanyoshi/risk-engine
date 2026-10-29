import gameboard
import numpy as np
import numpy.typing as npt
import territory

# Asks for a whole number between low and high. Returns None if the player enters nothing
def ask_int(prompt: str, low: int, high: int) -> int | None:
    while True:
        answer: str = input(prompt).strip()
        if answer == '':
            return None
        try:
            number: int = int(answer)
        except ValueError:
            print("Please enter a whole number.")
            continue
        if low <= number <= high:
            return number
        print(f"Enter a number between {low} and {high}.")

def deploy(board: gameboard.GameBoard, player: int) -> None:
    print_territories(board, player)
    print_continent_fraction(board, player)
    owned = board.owned(player)

    # Allow the player to draft to multiple places on the same turn
    deployed: int = board.deploy_count(player)
    while deployed:
        location: str = input(f"{gameboard.PLAYER_COLORS[player]}, you have {deployed} troops to deploy. Where are you deploying? ").strip().lower()
        if location == 'help':
            print_territories(board, player)
            continue

        i: int = territory.indexer(location)
        if i == -1:
            print("Invalid territory")
            continue
        if not owned[i]:
            print("You don't own that territory!")
            continue

        placing: int | None = ask_int(f"How many are you placing? (1 to {deployed}) ", 1, deployed)
        if placing is None:
            continue

        board.armies[i] += placing
        print(f"{placing} troops added to {location.title()}.")
        deployed -= placing

def attack(board: gameboard.GameBoard, player: int) -> None:
    # The player can keep attacking until they enter nothing
    while not board.is_won():
        owned = board.owned(player)
        start: str = input(f"{gameboard.PLAYER_COLORS[player]}, where would you like to attack from? (hit the enter key to end your attack phase, or help to see all territories' troops) ").strip().lower()

        if start == '':
            return
        elif start == 'help':
            print_territories(board, player)
            continue

        start_index: int = territory.indexer(start)
        if start_index == -1:
            print("Invalid territory")
            continue
        if not owned[start_index]:
            print("You do not own this territory. Please choose again.")
            continue
        if board.armies[start_index] < 2:
            print("You need at least 2 troops to attack from a territory.")
            continue

        # Calculate all targets and show them to the player
        possible_targets: npt.NDArray[np.bool] = territory.adjMatrix[start_index] & ~owned
        if not np.any(possible_targets):
            print("Cannot attack from there. Choose another territory")
            continue

        print("Possible targets:")
        for name, army, owner in zip(territory.territory_names[possible_targets], board.armies[possible_targets], board.owners[possible_targets]):
            print(f"{name.title()} ({gameboard.PLAYER_COLORS[owner]}) has {army} troops")

        final_target: str = input("What territory are you attacking? (Input nothing to choose a different start) ").strip().lower()
        if final_target == '':
            continue
        final_index: int = territory.indexer(final_target)
        if final_index == -1 or not possible_targets[final_index]:
            print("You cannot attack this territory.")
            continue

        max_troops: int = int(board.armies[start_index] - 1)
        attacking_troops: int | None = ask_int(f"How many troops? (1 to {max_troops}, nothing to cancel) ", 1, max_troops)
        if attacking_troops is None:
            continue

        defender: int = int(board.owners[final_index])
        board.battle(start_index, final_index, attacking_troops)
        print(f"Attacked {final_target.title()} from {start.title()} with {attacking_troops} troops")
        if board.owners[final_index] == player:
            print(f"You captured {final_target.title()}! It now has {board.armies[final_index]} troops.")
            if not board.is_alive(defender):
                print(f"{gameboard.PLAYER_COLORS[defender]} has been eliminated!")
        else:
            print(f"{final_target.title()} held with {board.armies[final_index]} troops left.")

def fortify(board: gameboard.GameBoard, player: int) -> None:
    owned = board.owned(player)
    while True:
        start: str = input(f"{gameboard.PLAYER_COLORS[player]}, where would you like to fortify from? (enter nothing to skip) ").strip().lower()
        if start == '':
            return
        elif start == 'help':
            print_territories(board, player)
            continue

        start_index: int = territory.indexer(start)
        if start_index == -1:
            print("Invalid territory")
            continue
        if not owned[start_index]:
            print("You do not own this territory.")
            continue
        if board.armies[start_index] < 2:
            print("You need at least 2 troops to move troops out of a territory.")
            continue

        # List out all possibilities to the player
        connection_matrix: npt.NDArray[np.bool] = territory.total_connections(start_index, owned)
        if not np.any(connection_matrix):
            print("That territory is not connected to any of your other territories.")
            continue
        print("You can fortify:")
        print(', '.join(np.strings.title(territory.territory_names[connection_matrix])))

        end: str = input("Where would you like to fortify? (enter nothing to choose a different start) ").strip().lower()
        if end == '':
            continue
        end_index: int = territory.indexer(end)
        if end_index == -1 or not connection_matrix[end_index]:
            print("You cannot fortify that territory.")
            continue

        max_troops: int = int(board.armies[start_index] - 1)
        placing: int | None = ask_int(f"How many troops are you sending? (1 to {max_troops}, nothing to cancel) ", 1, max_troops)
        if placing is None:
            continue

        board.fortify(start_index, end_index, placing)
        print(f"Moved {placing} troops from {start.title()} to {end.title()}.")
        return

def print_territories(board: gameboard.GameBoard, player: int) -> None:
    # List out all named territories, the player's own first and then each opponent's
    for other in [player] + [p for p in board.alive_players() if p != player]:
        owned = board.owned(other)
        names = np.strings.title(territory.territory_names[owned])
        soldiers = board.armies[owned].astype(str)
        heading = "Your" if other == player else f"{gameboard.PLAYER_COLORS[other]}'s"
        print(f"\n{heading} owned territories & troop counts:")
        print('\n'.join(np.strings.add(names + ', ', soldiers)))
    print()

def print_continent_fraction(board: gameboard.GameBoard, player: int) -> None:
    owned_per_continent = np.sum(territory.continents & board.owned(player), axis = 1)
    total_per_continent = np.sum(territory.continents, axis = 1)
    for name, owned, total in zip(territory.continent_names, owned_per_continent, total_per_continent):
        print(f"{owned} of {total} territories controlled in {name}")
