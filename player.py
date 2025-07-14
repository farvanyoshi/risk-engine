import territory
import numpy as np

def draft(drafted, board):
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
            

            while placing > drafted or -1:
                try:
                    placing = int(input(f"Invalid number of troops. Enter a number between 0 and {drafted}, or put nothing to go back: "))
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
    targets = []
    while start == '':
        start = input("Where would you like to attack from? (hit the enter key to end your attack phase, or help to see all your territories' troops) ").lower()

        if start == '':
            return
        elif start == 'help':
            start == ''
            print(list(zip(territory.territory_names, board.troop_array)))
            continue
        
        start_index = territory.indexer(start)

        if start_index == -1:
            continue
        
        possible_targets = territory.attackable(start_index, board.owners, 1)

        if possible_targets == None:
            start = ''
            continue
        if all(possible_targets == 0):
            print("Cannot attack from there. Place in another territory")
            continue
    
        print("Possible targets:\n", [(territory.territory_names[i], board.troop_array[i]) for i, owned in enumerate(targets) if owned])
        final_target = ''
        while not final_target:
            final_target = input("What territory are you attacking? ").lower()
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
                board.battle(territory.indexer(start), territory.indexer(final_target), attacking_troops)
        start = ''
            