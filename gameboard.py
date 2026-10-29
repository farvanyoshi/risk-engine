import numpy as np
import numpy.typing as npt
import territory

# Starting troops and owners for two players: every territory gets 1, 2, or 3 troops, and each side gets 21 territories
INIT_ARMIES: npt.NDArray[np.integer] = np.array([1, 2, 3] * 14)
INIT_OWNERS: npt.NDArray[np.bool] = np.array([0, 1] * 21, dtype = bool)

# Contains the common game code to both the player and AI
# owners[i] is True when the player owns territory i, and False when the AI owns it
class GameBoard:
    def __init__(self, armies: npt.NDArray[np.integer] | None = None, owners: npt.NDArray[np.bool] | None = None) -> None:
        # every new game gets its own shuffled copy, so boards never share arrays
        self.armies: npt.NDArray[np.integer] = np.random.permutation(INIT_ARMIES) if armies is None else armies
        self.owners: npt.NDArray[np.bool] = np.random.permutation(INIT_OWNERS) if owners is None else owners

    def copy(self):
        return GameBoard(self.armies.copy(), self.owners.copy())

    def owned(self, player: bool) -> npt.NDArray[np.bool]:
        return self.owners if player else ~self.owners

    # True if the player won, False if the AI won, None if the game is still going
    def winner(self) -> bool | None:
        if np.all(self.owners):
            return True
        if not np.any(self.owners):
            return False
        return None

    def is_won(self) -> bool:
        return self.winner() is not None

    # Troops given at the start of a turn: owned territories // 3 (minimum 3) plus continent bonuses
    def deploy_count(self, player: bool) -> int:
        return max(int(np.count_nonzero(self.owned(player))) // 3, 3) + territory.continent_bonus(player, self.owners)

    def can_attack(self, player: bool, start: int, end: int, attacking_troops: int) -> bool:
        owned = self.owned(player)
        return bool(
            owned[start] and not owned[end]
            and territory.adjMatrix[start][end]
            and 1 <= attacking_troops <= self.armies[start] - 1
        )

    def can_fortify(self, player: bool, start: int, end: int, transferring_troops: int) -> bool:
        owned = self.owned(player)
        return bool(
            owned[start] and start != end
            and territory.total_connections(start, owned)[end]
            and 1 <= transferring_troops <= self.armies[start] - 1
        )

    # Deterministic battle: the bigger side wins and keeps the difference
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
