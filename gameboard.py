import numpy as np
import numpy.typing as npt
#from interface import gui

# Create random troops and owners to start the game for two players
INIT_ARMIES: npt.NDArray[np.integer] = np.array([1, 2, 3] * 14)
INIT_OWNERS: npt.NDArray[np.bool] = np.array([0, 1] * 21, dtype = bool)

# Contains the common game code to both the player and AI
class GameBoard:
    def __init__(self, armies: npt.NDArray[np.integer] = INIT_ARMIES, owners: npt.NDArray[np.bool] = INIT_OWNERS) -> None:
        self.armies: npt.NDArray[np.integer] = armies
        self.owners: npt.NDArray[np.bool] = owners

        # if multiple gameboards are created, the original order must be shuffled
        np.random.shuffle(INIT_ARMIES)
        np.random.shuffle(INIT_OWNERS)

    def copy(self):
        return GameBoard(self.armies.copy(), self.owners.copy())

    def hash(self):
        return (tuple(self.owners), tuple(self.armies))

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