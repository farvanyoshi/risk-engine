from main import game
import territory

def draft(drafted, owners):
    print("Owned territories:\n", [territory.territory_names[i] for i, owned in enumerate(owners) if owned])
    # Allow the player to draft to multiple places on the same turn
    while drafted:
        location = input(f"You have {drafted} troops to deploy. Where are you deploying? ").lower()

        i = territory.indexer(location)
        if i == -1:
            print("Invalid territory.")
            continue

        if owners[i]:
            placing = int(input("How many are you placing? Enter just an integer: "))
            while placing > drafted:
                placing = int(input(f"Not enough troops for that. Put in a number less than {drafted} or nothing to go back: "))
            game.deploy(placing, location)
            print(f"{placing} troops added to {location}.")
        else:
            print("You don't own that territory!")

def prompt_attack():
    start = ''
    targets = []
    while start == '':
        start = input("Where would you like to attack from? (hit the enter key to skip your attack phase, or help to see all your territories) ").lower()

        if start == '':
            return
        
        targets = territory.attackable(territory.indexer(start), game.owners, 1)

        if targets == None:
            start = ''
        if all(targets == 0):
            print("Cannot attack from there. Place in another territory")
    
    target_names = [territory.territory_names[i] for i, owned in enumerate(targets) if owned]