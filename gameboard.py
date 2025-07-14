import engine
import numpy as np
import player
import territory

# Create random troops and owners to start the game for two players
init_troop_array = np.array([1, 2, 3] * 14)
init_owners = np.array([0, 1] * 21, dtype = bool)
np.random.shuffle(init_troop_array)
np.random.shuffle(init_owners)

# Contains the common game code to both the player and AI
class GameBoard:
    def __init__(self, player = init_owners[0], troop_array=init_troop_array, owners=init_owners):
        self.troop_array = troop_array
        self.owners = owners
        self.current_player: int = player
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
        print("It is now player " + str(self.current_player) + "'s turn" )
        drafted = int(max(np.count_nonzero(self.owners == self.current_player) // 3, 3) 
        + territory.continent_bonus(self.current_player, self.owners))

        if self.current_player == 1:
            player.draft(drafted, self)
            player.attack(self)
            player.fortify()
            self.current_player = 0
        elif self.current_player == 0:
            # engine.draft_attack_calculation(drafted)
            # engine.fortify()
            player.draft(drafted, self)
            player.attack(self)
            player.fortify()
            self.current_player = 1
        return
    
    def deploy(self, troops, location):
        self.owners[location] += troops

    def battle(self, start, end, attacking_troops):
        self.troop_array[start] -= attacking_troops
        if attacking_troops > self.troop_array[end]:
            self.troop_array[end] = attacking_troops - self.troop_array[end]
            self.owners[end] = not self.owners[end]
        elif attacking_troops == self.troop_array[end]:
            self.troop_array[end] = 1
        else:
            self.troop_array[end] -= attacking_troops

    def fortify(self, start, end, transferring_troops):
        self.troop_array[start] -= transferring_troops
        self.troop_array[end] += transferring_troops