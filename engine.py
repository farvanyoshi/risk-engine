import gameboard
import numpy as np
import numpy.typing as npt
import territory

MAX_POSSIBLE_BORDERS = 6
MIN_POSSIBLE_BORDERS = 2

connectivity: npt.NDArray[np.integer] = territory.adjMatrix.sum(1)
scaled_connectivity: npt.NDArray[np.floating] = (connectivity - MIN_POSSIBLE_BORDERS) / (MAX_POSSIBLE_BORDERS - MIN_POSSIBLE_BORDERS)

territory_to_continent: npt.NDArray[np.integer] = np.argmax(territory.continents, 0)
adjacent_in_continent: npt.NDArray[np.bool] = territory.continents[territory_to_continent]
non_continent_adjacency: npt.NDArray[np.bool] = territory.adjMatrix & ~adjacent_in_continent
total_foreign_connections: npt.NDArray[np.integer] = non_continent_adjacency.sum(axis = 1)
scaled_foreign_connections: npt.NDArray[np.integer] = (total_foreign_connections - min(total_foreign_connections)) / (max(total_foreign_connections) - min(total_foreign_connections))

def score_territories(board: gameboard.GameBoard, weights: npt.NDArray[np.floating] = np.array([1, 5/6, 2/3, 1/2, 1/3, 1/6])) -> tuple[npt.NDArray[np.floating], float]:
    ai_board = ~board.owners

    # shows which territories around a territory owned by the ai are owned by the player
    player_adjacency: npt.NDArray[np.bool] = territory.adjMatrix & board.owners

    # shows how much of each continent the ai has left
    engine_continents: npt.NDArray[np.bool] = territory.continents & ai_board
    continent_percents: npt.NDArray[np.integer] = engine_continents.sum(1) / territory.continents.sum(1) * 100
    scaled_continent_percents: npt.NDArray[np.floating] = continent_percents / max(continent_percents)

    # scaled_continent_precents maps out the percentage completed of a continent per continent, so it must be converted into per territory
    scaled_continent_per_territory: npt.NDArray[np.floating] = territory.continents.T @ scaled_continent_percents

    # sum armies of adjacent enemy troops and divide by troops in said territory to find threat level
    threat_level: npt.NDArray[np.integer] = (player_adjacency * board.armies).sum(1) / board.armies
    scaled_threat_level: npt.NDArray[np.integer] = threat_level / threat_level.max()

    # it is important to protect already held continents
    on_completed_continent: npt.NDArray[np.bool] = np.bitwise_or.reduce(territory.continents & ai_board)

    # a state with many allied borders is safer, but also less viable to attack from
    allied_borders: npt.NDArray[np.bool] = territory.adjMatrix & ai_board
    scaled_allied_borders: npt.NDArray[np.floating] = allied_borders.sum(1) / MAX_POSSIBLE_BORDERS

    params: npt.NDArray[np.floating] = (np.atleast_2d(weights).T * np.array((
        scaled_continent_per_territory,
        scaled_threat_level,
        on_completed_continent,
        scaled_foreign_connections,
        scaled_allied_borders,
        scaled_connectivity
    ))).sum(0)

    scaled_params: npt.NDArray[np.floating] = (params - params.min()) / (params.max() - params.min())

    sum_params: float = float(scaled_params.sum())

    return (scaled_params, sum_params)




'''
ai_draft_bonus: int = territory.continent_bonus(False, board.owners)
deploying: int = max(int(np.count_nonzero(ai_board)) // 3, 3) + ai_draft_bonus
'''