import gameboard
import numpy as np
import numpy.typing as npt
import scoring
import territory

DEPTH = 1

def deploy(board: gameboard.GameBoard, player: bool) -> None:
    owned = board.owners if player else ~board.owners
    # calculate the troops and territory scores for the ai
    ai_draft_bonus: int = territory.continent_bonus(False, owned)
    deploying: int = max(int(np.count_nonzero(~owned)) // 3, 3) + ai_draft_bonus
    scores = scoring.deploy_fortify_territory_scoring(board)

    # Places all the troops in the highest scoring territory
    board.armies[scores.argmax()] += deploying

def fortify(board: gameboard.GameBoard, player) -> None:
    scores: npt.NDArray[np.floating] = scoring.deploy_fortify_territory_scoring(board)

    owned = board.owners if player else ~board.owners

    # choose the ending territory to be the one with the highest score
    end: int = int((scores * owned).argmax())

    # find all territories connected to the end territory
    connections: npt.NDArray[np.bool] = territory.total_connections(end, owned)

    if not np.any(connections):
        return

    # move troops from the worst remaining territory
    start: int = int((scores)[connections].argmin())
    board.fortify(start, end, int((scores.max() - scores.min()) * board.armies[start]))

def attack(board: gameboard.GameBoard, player, depth: int = DEPTH):
    owned = board.owners if player else ~board.owners
    while True:
        best_score, best_board = minimax_attack(board, player, depth)
        if scoring.score_board(best_board, player) > best_score: # type: ignore
            board.owners = best_board.owners.copy()
            board.armies = best_board.armies.copy()
        else:
            break

def minimax_attack(board: gameboard.GameBoard, player: bool, depth: int) -> tuple[float, gameboard.GameBoard]:
    if depth == 0:
        return scoring.score_board(board, player), board

    owned = board.owners if player else ~board.owners
    best_score = scoring.score_board(board, player)
    best_board = board

    deploy(best_board, player)

    for start in np.flatnonzero(owned & (board.armies > 1)):
        adjacent_enemies = np.flatnonzero(territory.adjMatrix[start] & ~owned)
        for end in adjacent_enemies:
            if board.armies[start] > board.armies[end]:
                new_board = board.copy()
                new_board.battle(start, end, int(board.armies[start] - 1))
                score, result_board = minimax_attack(new_board, player, depth - 1)
                if score > best_score:
                    best_score = score
                    best_board = result_board

    fortify(best_board, player)

    return best_score, best_board



# basically this project is on par to be so goated and they will finish this project tonight and it is so easy to finish this project bc everyone is so locked in and this is so easy to code and print hello world and this is so much fun and this is so so so so so so so good and great because JCN is working on this so diligently
# by Shaurya