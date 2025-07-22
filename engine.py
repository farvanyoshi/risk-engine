import gameboard
import numpy as np
import numpy.typing as npt
import territory

MAX_POSSIBLE_BORDERS = 6
MIN_POSSIBLE_BORDERS = 2

def deploy_attack(board: gameboard.GameBoard) -> None:
    ai_draft_bonus: int = territory.continent_bonus(False, board.owners)
    deploying: int = max(int(np.count_nonzero(board.owners == board.is_player)) // 3, 3) + ai_draft_bonus

    ''' trying out code
    need a way to count all the enemy troops around a territory
    '''
    player_adjacency: npt.NDArray[np.bool] = territory.adjMatrix & board.owners

    threat_level: npt.NDArray[np.intp] = (player_adjacency * board.armies).sum(1) / board.armies
    offensive_possibility: npt.NDArray[np.intp] = player_adjacency.sum(1)
    connectivity: npt.NDArray[np.intp] = territory.adjMatrix.sum(1)

    # shows how much of each continent the ai has left
    engine_continents: npt.NDArray[np.bool] = territory.continents & ~board.owners
    continent_percents: npt.NDArray[np.intp] = engine_continents.sum(1) / territory.continents.sum(1) * 100

    # the weights to be used in this project
    normalized_connectivity: npt.NDArray[np.float64] = (connectivity - MIN_POSSIBLE_BORDERS) / (MAX_POSSIBLE_BORDERS - MIN_POSSIBLE_BORDERS)
    normalized_allied_borders: npt.NDArray[np.float64] = (territory.adjMatrix & ~board.owners).sum(1) / MAX_POSSIBLE_BORDERS
    normalized_continent_percents: npt.NDArray[np.float64] = continent_percents / max(continent_percents)
    normalized_threat_level: npt.NDArray[np.intp] = threat_level / threat_level.max()
    normalized_offensive_possibility: npt.NDArray[np.intp] = offensive_possibility / offensive_possibility.max()

