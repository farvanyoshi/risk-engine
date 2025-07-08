import random
from main import continentor, binator
import territory

init_troops = [1, 2, 3] * 14
init_owners = [0, 1] * 21

random.shuffle(init_troops)
random.shuffle(init_owners)

class GameBoard:
    def __init__(self, player=init_owners[0], troops=init_troops, owners=init_owners):
        self.troops = troops
        self.owners = owners
        self.player = player
        self.cards = [0, 0]
    
    def continentor(self):
        owned_string = binator(self.owners)
        player_bonus = 0
        if not self.player:
            owned_string = ~owned_string
        for continent, bonus in zip(territory.continents, territory.continent_bonuses):
            if owned_string & continent == continent:
                player_bonus += bonus
        return bonus

    def binator(self):
        new = 0
        for i in range(len(self.owners)):
            new += (self.owners[i] << (42 - i))
        return new

    def move(self):
        self.deploy(self.player, self.owners.count(self.player) // 3 + continentor(self.player))
        
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
            return (1 << i) & binator(self.owners[self.player])

        except:
            print("Invalid territory")
            return False
    

    def attack(start, end):
        pass