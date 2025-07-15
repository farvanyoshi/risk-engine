import numpy as np
import territory

def draft(drafted, board):
    print_territory(board)
    print_continent_fraction(board)
    # Allow the player to draft to multiple places on the same turn
    while drafted:
        location = input(f"You have {drafted} troops to deploy. Where are you deploying? ").lower()

        i = territory.indexer(location)
        if i == -1:
            print("Invalid territory")
            continue
        
        if ~(board.owners[i] ^ board.current_player):
            try:
                placing = int(input("How many are you placing? Enter just an integer: "))
            except ValueError:
                print("Please enter a positive integer.")
                continue
            
            # placing == -1 is an error handling value the input is not valid
            while placing > drafted or placing < 0:
                try:
                    placing = int(input(f"Invalid number of troops. Enter a number between 0 and {drafted}: "))
                except ValueError:
                    placing = -1
                    print("Please enter a positive integer.")
                    continue

            board.deploy(placing, i)
            print(f"{placing} troops added to {territory.capitalize_territory(location)}.")
            drafted -= placing
        else:
            print("You don't own that territory!")

def attack(board):
    start = ''
    while start == '':
        start = input("Where would you like to attack from? (hit the enter key to end your attack phase, or help to see all your territories' troops) ").lower()

        if start == '':
            return
        elif start == 'help':
            start == ''
            print_territory(board)
            continue
        
        start_index = territory.indexer(start)

        if start_index == -1:
            start = ''
            continue
        
        if board.owners[start_index] != board.current_player:
            print("You do not own this territory. Please choose again.")
            start = ''
            continue

        # Calculate all targets and show them to the player
        possible_targets = territory.attackable(start_index, board.owners, 1)
        if np.all(possible_targets == 0):
            print("Cannot attack from there. Choose another territory")
            start = ''
            continue
    
        target_names = ((territory.capitalize_territory(territory.territory_names[i]), int(board.armies[i])) for i, owned in enumerate(possible_targets) if owned != board.current_player)
        
        print("Possible targets:")
        for name, army in target_names:
            print(f"{name} has {army} troops")
        
        final_target = ''
        while True:
            final_target = input("What territory are you attacking? ").lower()
            final_index = territory.indexer(final_target)

            if final_index == -1:
                print("Not a valid place to attack.")
                continue
            if final_target not in possible_targets:
                print("You cannot attack this territory.")
                continue

            attacking_troops = 0
            while not attacking_troops:
                try:
                    troops = int(input("How many troops? "))
                    if attacking_troops < 0 or attacking_troops > board.armies[start_index] - 1:
                        attacking_troops = 0
                        print(f"Invalid number of troops. Please give an integer between 0 and {board.armies[start_index] - 1}")
                except ValueError:
                    attacking_troops = 0
                    print("Please enter a valid positive integer.")
                    continue
            if final_target in possible_targets:
                board.battle(territory.indexer(start_index), final_index, attacking_troops)
                print(f"Attacked {territory.capitalize_territory(final_target)} from {territory.capitalize_territory(start)} with {attacking_troops} troops")

def fortify(board):
    start_index = territory.indexer(input("Where would you like to fortify from? ").lower())
    while start_index == -1:
        start_index = territory.indexer(input("Not a valid territory. Please input another place: ").lower())
        continue

    # List out all possiblities to the player
    connection_matrix = territory.total_connections(start_index, board.owners, board.current_player)
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

def print_territory(board, val=[]):
    # List out all named territories to the player
    opponent_territories = []
    print("Your owned territories & troop counts:")
    if board.current_player:
        for i, owned in enumerate(board.owners):
            if owned:
                print(territory.capitalize_territory(territory.territory_names[i]) + ', ' + str(board.armies[i]))
            else:
                opponent_territories.append((territory.territory_names[i], int(board.armies[i])))
    else:
        for i, owned in enumerate(board.owners):
            if not owned:
                print(territory.capitalize_territory(territory.territory_names[i]) + ', ' + str(board.armies[i]))
            else:
                opponent_territories.append((territory.territory_names[i], int(board.armies[i])))

    
    print("\nOpponent's owned territories & troop counts:")
    for i, j in opponent_territories:
        print(territory.capitalize_territory(i) + ',', j)

def print_continent_fraction(board):
    if board.current_player:
        for i, continent in enumerate(territory.continents):
            print(sum(np.bitwise_and(continent, board.owners)), "of the", sum(continent), "territories in", territory.continent_names[i])
    else:
        for i, continent in enumerate(territory.continents):
            print(sum(np.bitwise_and(continent, np.bitwise_not(board.owners))), "of the", sum(continent), "territories in", territory.continent_names[i])
