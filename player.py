import territory

def draft(drafted, board):
    print("Owned territories:\n", [territory.territory_names[i] for i, owned in enumerate(board.owners) if owned])
    # Allow the player to draft to multiple places on the same turn
    while drafted:
        location = territory.capitalize_territory(input(f"You have {drafted} troops to deploy. Where are you deploying? "))

        i = territory.indexer(location)
        if i == -1:
            print("Invalid territory.")
            continue

        if board.owners[i]:
            try:
                placing = int(input("How many are you placing? Enter just an integer: "))
            except ValueError:
                print("Please enter a positive integer.")
                continue
            

            while placing > drafted:
                try:
                    placing = int(input(f"Not enough troops for that. Put in a number less than {drafted} or nothing to go back: "))
                except ValueError:
                    placing = 0
                    print("Please enter a positive integer.")
                    continue

            board.deploy(placing, i)
            print(f"{placing} troops added to {location}.")
            drafted -= placing
        else:
            print("You don't own that territory!")

def attack(board):
    start = ''
    targets = []
    while start == '':
        start = input("Where would you like to attack from? (hit the enter key to skip your attack phase, or help to see all your territories' troops) ").lower()

        if start == '':
            return
        elif start == 'help':
            print(zip(territory.territory_names, board.troop_array))
            continue
        
        targets = territory.attackable(territory.indexer(start), board.owners, 1)

        if targets == None:
            start = ''
            continue
        if all(targets == 0):
            print("Cannot attack from there. Place in another territory")
            continue
    
        print("Possible targets:\n", [(territory.territory_names[i], board.troop_array[i]) for i, owned in enumerate(targets) if owned])

