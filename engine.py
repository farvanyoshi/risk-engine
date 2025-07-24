import gameboard
import numpy as np
import numpy.typing as npt
import scoring
import territory

# def generate_possible_attacks(board: gameboard.GameBoard):
#     return [np.flatnonzero(board.armies > 1 & ~board.owners)]

def deploy(board: gameboard.GameBoard) -> None:
    # calculate the troops and territory scores for the ai
    ai_draft_bonus: int = territory.continent_bonus(False, board.owners)
    deploying: int = max(int(np.count_nonzero(~board.owners)) // 3, 3) + ai_draft_bonus
    scores = scoring.deploy_fortify_territory_scoring(board)

    # Places all the troops in the highest scoring territory
    board.armies[scores.argmax()] += deploying

def fortify(board: gameboard.GameBoard) -> None:
    scores: npt.NDArray[np.floating] = scoring.deploy_fortify_territory_scoring(board)

    # choose the ending territory to be the one with the highest score
    end: int = int((scores * board.owners).argmax())

    # find all territories connected to the end territory
    connections: npt.NDArray[np.bool] = territory.total_connections(end, ~board.owners)

    # move troops from the worst remaining territory
    start: int = int((scores)[connections].argmin())
    board.fortify(start, end, int((scores.max() - scores.min()) * board.armies[start]))

def minimax(board: gameboard.GameBoard, depth: int, for_engine: bool):

    if depth == 0 or board.is_won():
        return scoring.score_board(board)
    
    best_score = -np.inf if for_engine else np.inf
    best_move = None

    # TODO: Implement recursion through the minimax tree

# basically this project is on par to be so goated and they will finish this project tonight and it is so easy to finish this project bc everyone is so locked in and this is so easy to code and print hello world and this is so much fun and this is so so so so so so so good and great because JCN is working on this so diligently
# by Shaurya