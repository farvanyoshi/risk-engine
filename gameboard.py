import random
import territory
import numpy as np

init_troop_array = np.array([1, 2, 3] * 14)
init_owners = np.array([0, 1] * 21, dtype = bool)

np.random.shuffle(init_troop_array)
np.random.shuffle(init_owners)

class GameBoard:
    def __init__(self, player=init_owners[0], troop_array=init_troop_array, owners=init_owners):
        self.troop_array = troop_array
        self.owners = owners
        self.current_player = 1 # Use for testing
        self.cards = [0, 0]
    
    def won(self):
        if np.all(self.owners == 0):
            print("The AI has won the game!")
            return True
        elif np.all(self.owners == 1):
            print("The player has won the game!")
            return True
        return False

    def move(self):
        self.player_draft(np.count_nonzero(self.owners == self.current_player) // 3 + territory.continent_bonus(self.current_player, self.owners))
        self.prompt_attack()
    

    def player_draft(self, drafted):
        if self.current_player != 0: # fix later for ai

            # Allow the player to draft to multiple places on the same turn
            while drafted:
                location = input(f"You have {drafted} troops drafted. Where are you deploying: ")

                i = territory.indexer(location)
                if i == -1:
                    print("Invalid territory.")
                    continue

                if self.owners[i] == self.current_player:
                    placing = int(input("How many are you placing? Enter just an integer: "))
                    while placing > drafted:
                        placing = input(f"Not enough troops for that. Put in a number less than {self.troop_array} or nothing to go back: ")
                    self.troop_array[i] += placing
                    drafted -= placing
                    print(f"{placing} troops placed in {location}.")
                else:
                    print("You don't own that territory!")

    

    def prompt_attack(self):
        start = ''
        targets = []
        while start == '':
            start = input("Where would you like to attack from? (hit the enter key to skip your attack phase, or help to see all your territories)")

            # Write out all of the territories owned by the player
            if start == '':
                return
            if start == 'help':
                for i, owned in enumerate(self.owners):
                    if owned: 
                        print(territory.territory_names[i])
            
            targets = self.attackable(start)
            if targets == None:
                print("There is nothing you can attack from here.")
                start = ''
        
    def attackable(self, terr):
        if self.player == 1:
            return np.bitwise_and(territory.adjMatrix[terr], np.bitwise_not(self.owners))
        else:
            return np.bitwise_and(territory.adjMatrix[terr], self.owners)
        
    def battle(self, start, end, attacking_troops):
        if attacking_troops > self.troop_array[end]:
            self.troop_array[end] = -(self.troop_array[end]-attacking_troops)
            self.owners[end] = self.current_player
        elif attacking_troops == self.troop_array[end]:
            self.troop_array[end] = 1
        else:
            self.troop_array[end] -= attacking_troops
            self.troop_array[start] -= attacking_troops