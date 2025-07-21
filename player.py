import gameboard
import numpy as np
import numpy.typing as npt
import territory

def draft(board: gameboard.GameBoard) -> None:
    print_territories(board)
    print_continent_fraction(board)

    # Allow the player to draft to multiple places on the same turn
    drafted: int = max(int(np.count_nonzero(board.owners == board.is_player) // 3), 3) + territory.continent_bonus(board.is_player, board.owners)
    while drafted:
        location: str = input(f"You have {drafted} troops to deploy. Where are you deploying? ").strip().lower()

        i: int = territory.indexer(location)
        if i == -1:
            print("Invalid territory")
            continue
        
        if board.owners[i]:
            try:
                placing: int = int(input("How many are you placing? Enter just an integer: "))
            except ValueError:
                print("Please enter a positive integer.")
                continue
            
            # placing == -1 is an error handling value for when the input is not valid
            while placing > drafted or placing < 0:
                try:
                    placing = int(input(f"Invalid number of troops. Enter a number between 0 and {drafted}: "))
                except ValueError:
                    placing = -1
                    print("Please enter a positive integer.")
                    continue

            board.armies[i] += placing
            print(f"{placing} troops added to {location.title()}.")
            drafted -= placing
        else:
            print("You don't own that territory!")

def attack(board) -> None:
    start: str = ''
    while start == '':
        start = input("Where would you like to attack from? (hit the enter key to end your attack phase, or help to see all your territories' troops) ").lower()

        if start == '':
            return
        elif start == 'help':
            start == '' # type: ignore
            print_territories(board)
            continue
        
        start_index: int = territory.indexer(start)

        if start_index == -1:
            start = ''
            continue
        
        if not board.owners[start_index]:
            print("You do not own this territory. Please choose again.")
            start = ''
            continue

        # Calculate all targets and show them to the player
        possible_targets: np.ndarray = territory.adjMatrix[start_index] & (board.owners if board.is_player else ~board.owners)

        if np.all(possible_targets == 0):
            print("Cannot attack from there. Choose another territory")
            start = ''
            continue
    
        target_names: np.ndarray = np.column_stack(territory.territory_names[possible_targets], board.armies[possible_targets]) # type: ignore

        print("Possible targets:")
        for name, army in target_names:
            print(f"{name} has {army} troops")
        
        final_target: str = ''
        while True:
            final_target: str = input("What territory are you attacking? (Input nothing to move on)").lower()
            if final_target == '':
                break
            final_index: int = territory.indexer(final_target)

            if final_index == -1:
                print("Not a valid place to attack.")
                continue
            if final_target not in possible_targets:
                print("You cannot attack this territory.")
                continue

            attacking_troops: int = 0
            while not attacking_troops:
                try:
                    attacking_troops = int(input("How many troops? "))
                    if attacking_troops < 0 or attacking_troops > board.armies[start_index] - 1:
                        attacking_troops = 0
                        print(f"Invalid number of troops. Please give an integer between 0 and {board.armies[start_index] - 1}")
                except ValueError:
                    attacking_troops = 0
                    print(f"Invalid number of troops. Please give an integer between 0 and {board.armies[start_index] - 1}")
            if final_target in possible_targets:
                board.battle(start_index, final_index, attacking_troops)
                print(f"Attacked {final_target.title()} from {start.title()} with {attacking_troops} troops")

def fortify(board):
    start_index: int = territory.indexer(input("Where would you like to fortify from? ").lower())
    while start_index == -1:
        start_index = territory.indexer(input("Not a valid territory. Please input another place: ").lower())
        continue

    # List out all possiblities to the player
    connection_matrix = territory.total_connections(start_index, board.owners, True)
    connections = (territory.territory_names[index] for index, connected in enumerate(connection_matrix) if connected)
    print(f"You can fortify:\n {connections}")

    end = input("Where would you like to fortify? ")
    while end not in connections:
        print("Invalid territory")
        end = input("Where would you like to fortify? ")

    end_index = territory.indexer(end)

    placing = -1
    max_troops = board.armies[start_index] - 1
    while placing:
        try:
            placing = int(input(f"How many troops are you sending? You have {max_troops} troops available to fortify. "))
        except ValueError:
            print("Please enter a positive integer.")
            continue

        if placing > max_troops:
            print("You don't have that many troops.")
            continue  

    board.fortify(start_index, end_index, max_troops)

def print_territories(board):
    # List out all named territories to the player
    names = np.strings.title(territory.territory_names[board.owners])
    soldiers = board.armies[board.owners].astype(str)
    print("Your owned territories & troop counts:")
    print('\n'.join(np.strings.add(names + ', ', soldiers)))

    opp_names = np.strings.title(territory.territory_names[~board.owners])
    opp_soldiers = board.armies[~board.owners].astype(str)    
    print("\nOpponent's owned territories & troop counts:")
    print('\n'.join(np.strings.add(opp_names + ', ', opp_soldiers)))
    

def print_continent_fraction(board):
    owned_per_continent = np.sum(territory.continents & board.owners, axis = 1)
    total_per_continent = np.sum(territory.continents, axis = 1)
    for name, owned, total in zip(territory.continent_names, owned_per_continent, total_per_continent):
        print(f"{owned} of {total} territories controlled in {name}")