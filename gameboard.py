import numpy as np
import numpy.typing as npt
from interface import gui

# Create random troops and owners to start the game for two players
init_armies: npt.NDArray[np.intp] = np.array([1, 2, 3] * 14)
init_owners: npt.NDArray[np.bool] = np.array([0, 1] * 21, dtype = bool)
np.random.shuffle(init_armies)
np.random.shuffle(init_owners)

# Contains the common game code to both the player and AI
class GameBoard:
    def __init__(self, armies: npt.NDArray[np.intp] = init_armies, owners: npt.NDArray[np.bool] = init_owners) -> None:
        self.armies: npt.NDArray[np.intp] = armies
        self.owners: npt.NDArray[np.bool] = owners
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