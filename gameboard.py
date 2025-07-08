import random
import territory
import numpy as np

init_troops = np.array([1, 2, 3] * 14)
init_owners = np.array([0, 1] * 21)

np.random.shuffle(init_troops)
np.random.shuffle(init_owners)

class GameBoard:
    def __init__(self, player=init_owners[0], troops=init_troops, owners=init_owners):
        self.troops = troops
        self.owners = owners
        self.player = player
        self.cards = [0, 0]
        self.move()
    
    def continentor(self):
        player_bonus = 0
        for continent, bonus in zip(territory.continents, territory.continent_bonuses):
            if self.player:
                if self.owners & continent == continent:
                    player_bonus += bonus
            else:
                if np.bitwise_not(self.owners) & continent == continent:
                    player_bonus += bonus
        return bonus

    def move(self):
        self.deploy(self.owners.count(self.player) // 3 + self.continentor(self.player))
        
    def deploy(self, troops):
        if self.player != 0:
            while troops:
                location = input(f"You have {troops} troops. Where are you deploying?")
                if self.check_owned(location, self.player):
                    break
                
            
    def check_owned(self, location):
        if self.player == 0:
            gameboard = ~gameboard
        
        try:
            i = territory.territory_names.index(location)
            return np.bitwise_and((1 << i), self.binator(self.owners[self.player]))

        except:
            print("Invalid territory")
            return False
    

    def attack(start, end):
        pass