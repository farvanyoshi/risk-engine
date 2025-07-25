import gameboard
import numpy as np
import numpy.typing as npt
import territory

MAX_POSSIBLE_BORDERS = 6
MIN_POSSIBLE_BORDERS = 2

# weights for each stage, used in evaluation
DEPLOY_WEIGHTS: npt.NDArray[np.floating] = np.array((1, 2/3, 1/3))
ATTACK_WEIGHTS: npt.NDArray[np.floating] = np.array((1, 4/5, 3/5, 2/5, 1/5))
FORTIFY_WEIGHTS: npt.NDArray[np.floating] = np.array(())

OPTIMAL_BORDERING_RATIO = 0.5

# more connected territories are more useful to attack, but harder to defend
connectivity: npt.NDArray[np.integer] = territory.adjMatrix.sum(1)
scaled_connectivity: npt.NDArray[np.floating] = (connectivity - MIN_POSSIBLE_BORDERS) / (MAX_POSSIBLE_BORDERS - MIN_POSSIBLE_BORDERS)

# need to hold choke points, so the toal connections out of continent should be known
territory_to_continent: npt.NDArray[np.integer] = np.argmax(territory.continents, 0)
adjacent_in_continent: npt.NDArray[np.bool] = territory.continents[territory_to_continent]
non_continent_adjacency: npt.NDArray[np.bool] = territory.adjMatrix & ~adjacent_in_continent
total_foreign_connections: npt.NDArray[np.integer] = non_continent_adjacency.sum(axis = 1)
scaled_foreign_connections: npt.NDArray[np.integer] = (total_foreign_connections - min(total_foreign_connections)) / (max(total_foreign_connections) - min(total_foreign_connections))

'''
In both the deploy and fortify sections of the code,
the AI will try to play more defensively.
This prevents the AI from overextending itself.
On the other hand, the attack phase 
'''

def scale(params: npt.NDArray[np.floating]) -> npt.NDArray[np.floating]:
    mn: np.floating = params.min()
    return (params - mn) / (params.max() - mn)

def allying_score(owners: npt.NDArray[np.bool]) -> npt.NDArray[np.floating]:
    num_neighboring_allies: npt.NDArray[np.integer] = (territory.adjMatrix & owners).sum(1)
    ally_ratio: npt.NDArray[np.floating] = num_neighboring_allies / connectivity

    return np.where(
        ally_ratio <= OPTIMAL_BORDERING_RATIO,
        ally_ratio / OPTIMAL_BORDERING_RATIO,
        (1 - ally_ratio) / (1 - OPTIMAL_BORDERING_RATIO)
    )

def def_params(board: gameboard.GameBoard) -> npt.NDArray[np.floating]:
    ai_board: npt.NDArray[np.bool] = ~board.owners

    # sum armies of adjacent enemy troops and divide by troops in said territory to find threat level
    board.armies[np.flatnonzero(board.armies == 0)] = 1
    threat_level: npt.NDArray[np.integer] = ((territory.adjMatrix & board.owners) * board.armies).sum(1) / board.armies
    scaled_threat_level: npt.NDArray[np.floating] = threat_level / (threat_level.max() or 1)

    # it is important to protect already held continents
    on_completed_continent: npt.NDArray[np.bool] = np.bitwise_or.reduce(territory.continents & ai_board)

    return np.array((scaled_threat_level, on_completed_continent, scaled_foreign_connections), dtype=float)

def deploy_fortify_territory_scoring(board: gameboard.GameBoard, weights: npt.NDArray[np.floating] = DEPLOY_WEIGHTS):
    params: npt.NDArray[np.floating] = (np.atleast_2d(weights).T * def_params(board)).sum(0)
    return scale(params)

def attack_territory_scoring(board: gameboard.GameBoard, player: bool, weights = ATTACK_WEIGHTS) -> npt.NDArray[np.floating]:
    owned = board.owners if player else ~board.owners
    # shows how much of each continent the ai has left
    engine_continents: npt.NDArray[np.bool] = territory.continents & owned
    continent_percents: npt.NDArray[np.integer] = engine_continents.sum(1) / territory.continents.sum(1) * 100
    scaled_continent_percents: npt.NDArray[np.floating] = continent_percents / (max(continent_percents) or 1)

    # scaled_continent_precents maps out the percentage completed of a continent per continent, so it must be converted into per territory
    scaled_continent_per_territory: npt.NDArray[np.floating] = territory.continents.T @ scaled_continent_percents

    # sorted by relative importance
    base_params = def_params(board)
    params: npt.NDArray[np.floating] = (np.atleast_2d(weights).T * np.array((
        scaled_continent_per_territory,
        base_params[0],
        base_params[1],
        base_params[2],
        scaled_connectivity
    ))).sum(0)

    return scale(params)

def score_board(board: gameboard.GameBoard, player: bool) -> float:
    return attack_territory_scoring(board, player).sum()