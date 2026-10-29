import gameboard
import numpy as np
import numpy.typing as npt
import territory

MAX_POSSIBLE_BORDERS = 6
MIN_POSSIBLE_BORDERS = 2

# weights for each stage, used in evaluation
DEPLOY_WEIGHTS: npt.NDArray[np.floating] = np.array((1, 2/3, 1/3))
ATTACK_WEIGHTS: npt.NDArray[np.floating] = np.array((1, 4/5, 3/5, 2/5, 1/5))

# how much a board score values territories, troops, and continent bonuses
BOARD_WEIGHTS: npt.NDArray[np.floating] = np.array((1, 1, 1))

OPTIMAL_BORDERING_RATIO = 0.5

# more connected territories are more useful to attack, but harder to defend
connectivity: npt.NDArray[np.integer] = territory.adjMatrix.sum(1)
scaled_connectivity: npt.NDArray[np.floating] = (connectivity - MIN_POSSIBLE_BORDERS) / (MAX_POSSIBLE_BORDERS - MIN_POSSIBLE_BORDERS)

# need to hold choke points, so the total connections out of continent should be known
territory_to_continent: npt.NDArray[np.integer] = np.argmax(territory.continents, 0)
adjacent_in_continent: npt.NDArray[np.bool] = territory.continents[territory_to_continent]
non_continent_adjacency: npt.NDArray[np.bool] = territory.adjMatrix & ~adjacent_in_continent
total_foreign_connections: npt.NDArray[np.integer] = non_continent_adjacency.sum(axis = 1)
scaled_foreign_connections: npt.NDArray[np.floating] = (total_foreign_connections - min(total_foreign_connections)) / (max(total_foreign_connections) - min(total_foreign_connections))

'''
In both the deploy and fortify sections of the code,
the AI will try to play more defensively.
This prevents the AI from overextending itself.
On the other hand, the attack phase values taking territories and continents.
'''

def scale(params: npt.NDArray[np.floating]) -> npt.NDArray[np.floating]:
    mn: np.floating = params.min()
    spread: np.floating = params.max() - mn
    return (params - mn) / spread if spread else np.zeros_like(params)

def allying_score(owners: npt.NDArray[np.bool]) -> npt.NDArray[np.floating]:
    num_neighboring_allies: npt.NDArray[np.integer] = (territory.adjMatrix & owners).sum(1)
    ally_ratio: npt.NDArray[np.floating] = num_neighboring_allies / connectivity

    return np.where(
        ally_ratio <= OPTIMAL_BORDERING_RATIO,
        ally_ratio / OPTIMAL_BORDERING_RATIO,
        (1 - ally_ratio) / (1 - OPTIMAL_BORDERING_RATIO)
    )

def def_params(board: gameboard.GameBoard, player: bool) -> npt.NDArray[np.floating]:
    owned: npt.NDArray[np.bool] = board.owned(player)

    # sum armies of adjacent enemy troops and divide by troops in said territory to find threat level
    armies: npt.NDArray[np.integer] = np.maximum(board.armies, 1)
    threat_level: npt.NDArray[np.floating] = ((territory.adjMatrix & ~owned) * armies).sum(1) / armies
    scaled_threat_level: npt.NDArray[np.floating] = threat_level / (threat_level.max() or 1)

    # it is important to protect already held continents
    held_continents: npt.NDArray[np.bool] = np.all(owned & territory.continents == territory.continents, axis = 1)
    on_completed_continent: npt.NDArray[np.bool] = territory.continents[held_continents].any(0)

    return np.array((scaled_threat_level, on_completed_continent, scaled_foreign_connections), dtype = float)

# Scores only the player's own territories; enemy territories get -inf so they are never picked
def deploy_fortify_territory_scoring(board: gameboard.GameBoard, player: bool, weights: npt.NDArray[np.floating] = DEPLOY_WEIGHTS) -> npt.NDArray[np.floating]:
    params: npt.NDArray[np.floating] = (np.atleast_2d(weights).T * def_params(board, player)).sum(0)
    return np.where(board.owned(player), scale(params), -np.inf)

def attack_territory_scoring(board: gameboard.GameBoard, player: bool, weights = ATTACK_WEIGHTS) -> npt.NDArray[np.floating]:
    owned = board.owned(player)
    # shows how much of each continent the player has
    engine_continents: npt.NDArray[np.bool] = territory.continents & owned
    continent_percents: npt.NDArray[np.floating] = engine_continents.sum(1) / territory.continents.sum(1) * 100
    scaled_continent_percents: npt.NDArray[np.floating] = continent_percents / (max(continent_percents) or 1)

    # scaled_continent_percents maps out the percentage completed of a continent per continent, so it must be converted into per territory
    scaled_continent_per_territory: npt.NDArray[np.floating] = territory.continents.T @ scaled_continent_percents

    # sorted by relative importance
    base_params = def_params(board, player)
    params: npt.NDArray[np.floating] = (np.atleast_2d(weights).T * np.array((
        scaled_continent_per_territory,
        base_params[0],
        base_params[1],
        base_params[2],
        scaled_connectivity
    ))).sum(0)

    return scale(params)

# Higher is better for the given player: valuable territories held, share of all troops, and continent bonuses
def score_board(board: gameboard.GameBoard, player: bool, weights: npt.NDArray[np.floating] = BOARD_WEIGHTS) -> float:
    if board.is_won():
        return np.inf if board.winner() == player else -np.inf

    owned = board.owned(player)
    territory_value: float = float((1 + attack_territory_scoring(board, player))[owned].sum()) / 42
    troop_share: float = float(board.armies[owned].sum() / board.armies.sum())
    bonus_share: float = territory.continent_bonus(player, board.owners) / float(territory.continent_bonuses.sum())

    return float(weights @ np.array((territory_value, troop_share, bonus_share)))
