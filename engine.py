import gameboard
import numpy as np
import numpy.typing as npt
import territory

MAX_POSSIBLE_BORDERS = 6
MIN_POSSIBLE_BORDERS = 2

def deploy_attack(board: gameboard.GameBoard) -> None:
    ai_board = ~board.owners
    ai_draft_bonus: int = territory.continent_bonus(False, board.owners)
    deploying: int = max(int(np.count_nonzero(ai_board)) // 3, 3) + ai_draft_bonus

    ''' trying out code
    need a way to count all the enemy troops around a territory
    '''
    player_adjacency: npt.NDArray[np.bool] = territory.adjMatrix & board.owners

    # shows how much of each continent the ai has left
    engine_continents: npt.NDArray[np.bool] = territory.continents & ai_board
    continent_percents: npt.NDArray[np.intp] = engine_continents.sum(1) / territory.continents.sum(1) * 100
    scaled_continent_percents: npt.NDArray[np.float64] = continent_percents / max(continent_percents)

    threat_level: npt.NDArray[np.intp] = (player_adjacency * board.armies).sum(1) / board.armies
    scaled_threat_level: npt.NDArray[np.intp] = threat_level / threat_level.max()

    on_completed_conntinent: npt.NDArray[np.bool] = np.bitwise_or.reduce(territory.continents & ai_board)

    allied_borders: npt.NDArray[np.bool] = territory.adjMatrix & ai_board
    scaled_allied_borders: npt.NDArray[np.float64] = allied_borders.sum(1) / MAX_POSSIBLE_BORDERS

    connectivity: npt.NDArray[np.intp] = territory.adjMatrix.sum(1)
    scaled_connectivity: npt.NDArray[np.float64] = (connectivity - MIN_POSSIBLE_BORDERS) / (MAX_POSSIBLE_BORDERS - MIN_POSSIBLE_BORDERS)


    # the weights to be used in this project
    continent_weight: float = 1
    threat_weight: float = 0.833
    comp_cont_weight: float = 0.667
    foreign_conn_weight: float = 0.5

