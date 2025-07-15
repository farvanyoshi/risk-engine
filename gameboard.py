import engine
import numpy as np
import player
import territory

# Create random troops and owners to start the game for two players
init_armies = np.array([1, 2, 3] * 14)
init_owners = np.array([0, 1] * 21, dtype = bool)
np.random.shuffle(init_armies)
np.random.shuffle(init_owners)

# Contains the common game code to both the player and AI
class GameBoard:
    def __init__(self, player = init_owners[0], armies=init_armies, owners=init_owners):
        self.armies = armies
        self.owners = owners
        self.current_player = player # Whoever owns afghanistan goes first for some reason
        self.cards = [0, 0]
    
    def is_won(self):
        if np.all(self.owners == 0):
            print("The AI has won the game!")
            return True
        elif np.all(self.owners == 1):
            print("The player has won the game!")
            return True
        return False

    def initiate_turn(self):
        print("It is now player " + str(1 if self.current_player else 0) + "'s turn" )
        drafted = int(max(np.count_nonzero(self.owners == self.current_player) // 3, 3) 
        + territory.continent_bonus(self.current_player, self.owners))

        if self.current_player == 1:
            player.draft(drafted, self)
            player.attack(self)
            player.fortify(self)
            self.current_player = 0
        elif self.current_player == 0:
            # engine.draft_attack_calculation(drafted)
            # engine.fortify()
            player.draft(drafted, self)
            player.attack(self)
            player.fortify(self)
            self.current_player = 1
        return
    
    def deploy(self, troops, location):
        self.armies[location] += troops

    def battle(self, start, end, attacking_troops):
        self.armies[start] -= attacking_troops
        if attacking_troops > self.armies[end]:
            self.armies[end] = attacking_troops - self.armies[end]
            self.owners[end] = not self.owners[end]
        elif attacking_troops == self.armies[end]:
            self.armies[end] = 1
        else:
            self.armies[end] -= attacking_troops

    def fortify(self, start, end, transferring_troops):
        self.armies[start] -= transferring_troops
        self.armies[end] += transferring_troops