import random
import territory
import numpy as np

init_troops = np.array([1, 2, 3] * 14)
init_owners = np.array([0, 1] * 21, dtype = bool)

np.random.shuffle(init_troops)
np.random.shuffle(init_owners)

class GameBoard:
    def __init__(self, player=init_owners[0], troops=init_troops, owners=init_owners):
        self.troops = troops
        self.owners = owners
        self.current_player = player
        self.cards = [0, 0]
    
    def won(self):
        if np.all(self.owners == 0):
            print("The AI has won the game!")
            return True
        elif np.all(self.owners == 1):
            print("The player has won the game!")
            return True
        return False

    def continentor(self):
        player_bonus = 0
        reverse_owners = np.bitwise_not(self.owners)
        for i, continent in enumerate(territory.continents):
            if self.current_player:
                if (np.bitwise_and(self.owners, continent) == continent).all():
                    player_bonus += territory.continent_bonuses[i]
            else:
                if (np.bitwise_and(reverse_owners, continent) == continent).all():
                    player_bonus += territory.continent_bonuses[i]
        return player_bonus

    def move(self):
        self.deploy(np.count_nonzero(self.owners == self.current_player) // 3 + self.continentor(self.current_player))
        self.attack()
        
    def deploy(self, drafted):
        if self.current_player != 0: # fix later for ai
            while drafted:
                location = input(f"You have {drafted} troops drafted. Where are you deploying?")
                i = territory.indexer(location)
                if self.owners[i] == self.current_player:
                    placing = int(input("How many are you placing? Enter just an integer."))
                    if placing > drafted:
                        print("You don't have that many troops!")
                        continue
                    self.troops[i] += placing
                    drafted -= placing
                    print(f"{drafted} troops placed in {location}.")
                else:
                    print("You don't own that territory!")

    def attack():
        start = -1
        while start < 0:
            start = territory.indexer(input("Where would you like to attack from?"))
        
    def attackble():
        pass
    
    def battle():
        pass

