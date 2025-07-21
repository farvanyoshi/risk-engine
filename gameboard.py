import engine
import numpy as np
import player
import territory
from .interface.gui import *

# Create random troops and owners to start the game for two players
init_armies: np.ndarray = np.array([1, 2, 3] * 14)
init_owners: np.ndarray = np.array([0, 1] * 21, dtype = bool)
np.random.shuffle(init_armies)
np.random.shuffle(init_owners)

# Contains the common game code to both the player and AI
class GameBoard:
    def __init__(self, armies: np.ndarray = init_armies, owners: np.ndarray = init_owners) -> None:
        self.armies: np.ndarray = armies
        self.owners: np.ndarray = owners
        self.is_player: bool = owners[0] # Whoever owns afghanistan goes first for some reason
    
    def is_won(self) -> bool:
        if np.all(self.owners == 0):
            print("The AI has won the game!")
            return True
        elif np.all(self.owners == 1):
            print("The player has won the game!")
            return True
        return False

    def battle(self, start: int, end: int, attacking_troops: int) -> None:
        self.armies[start] -= attacking_troops
        if attacking_troops > self.armies[end]:
            self.armies[end] = attacking_troops - self.armies[end]
            self.owners[end] = not self.owners[end]
        elif attacking_troops == self.armies[end]:
            self.armies[end] = 1
        else:
            self.armies[end] -= attacking_troops

    def fortify(self, start: int, end: int, transferring_troops: int) -> None:
        self.armies[start] -= transferring_troops
        self.armies[end] += transferring_troops