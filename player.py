import numpy as np
import territory

def draft(drafted, board):
    # List out all named territories to the player
    print("Owned territories & troop counts:")
    for i, owned in enumerate(board.owners):
        if owned:
            print(territory.capitalize_territory(territory.territory_names[i]) + ', ' + str(board.troop_array[i]))
    for i, continent in enumerate(territory.continents):
        print(sum(np.bitwise_and(continent, board.owners)), "of the", sum(continent), "territories in", territory.continent_names[i])
    
    # Allow the player to draft to multiple places on the same turn
    while drafted:
        location = input(f"You have {drafted} troops to deploy. Where are you deploying? ").lower()

        i = territory.indexer(location)
        if i == -1:
            print("Invalid territory")
            continue
        
        if board.owners[i]:
            try:
                placing = int(input("How many are you placing? Enter just an integer: "))
            except ValueError:
                print("Please enter a positive integer.")
                continue
            
            # placing == -1 is an error handling value the input is not valid
            while placing > drafted or placing == -1:
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
    start_index = ''
    targets = []
    while start_index == '':
        start_index = input("Where would you like to attack from? (hit the enter key to end your attack phase, or help to see all your territories' troops) ").lower()

        if start_index == '':
            return
        elif start_index == 'help':
            start_index == ''
            print(list(zip(territory.territory_names, board.troop_array)))
            continue
        
        start_index = territory.indexer(start_index)

        if start_index == -1:
            continue
        
        # Calculate all targets and show them to the player
        possible_targets = territory.attackable(start_index, board.owners, 1)
        if np.all(possible_targets == 0):
            print("Cannot attack from there. Choose another territory")
            continue
    
        print("Possible targets:\n", [(territory.territory_names[i], board.troop_array[i]) for i, owned in enumerate(targets) if owned])
        final_target = ''
        while not final_target:
            final_target = input("What territory are you attacking? ").lower()
            final_index = territory.indexer(final_target)
            while final_index == -1:
                final_target = input("Not a valid place to attack. Please enter something else: ").lower()
            attacking_troops = 0
            while not attacking_troops:
                try:
                    attacking_troops = int(input("How many troops? "))
                except ValueError:
                    attacking_troops = 0
                    print("Please enter a positive integer.")
                    final_target = ''
                    continue
            if final_target in possible_targets:
                board.battle(territory.indexer(start_index), final_index, attacking_troops)
        start_index = ''

def fortify(board):
    start_index = territory.indexer(input("Where would you like to fortify from? ").lower())
    while start_index == -1:
        start_index = territory.indexer(input("Not a valid territory. Please input another place: ").lower())
        continue

    # List out all possiblities to the player
    connections = territory.total_connections(start_index, board.owners)
    print(f"You can fortify:\n {connections}")

    end = input("Where would you like to fortify? ")
    while end not in connections:
        print("Invalid territory")
        end = input("Where would you like to fortify? ")

    end_index = territory.indexer(end)

    placing = -1
    max_troops = board.troop_array[start_index] - 1
    while placing:
        try:
            placing = int(input(f"How many troops are you sending? You have {max_troops} troops available to fortify. "))
        except ValueError:
            placing = -1
            print("Please enter a positive integer.")
            continue

        if placing > max_troops:
            placing = -1
            print("You don't have that many troops.")
            continue  

    board.fortify(start_index, end_index, max_troops)
    