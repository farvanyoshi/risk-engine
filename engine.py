from collections import deque
import gameboard
import numpy as np
import numpy.typing as npt
import scoring
import territory

def deploy(board: gameboard.GameBoard, player: bool) -> None:
    player_owned = board.owners if player else ~board.owners
    # calculate the troops and territory scores for the ai
    ai_draft_bonus: int = territory.continent_bonus(False, player_owned)
    deploying: int = max(int(np.count_nonzero(~player_owned)) // 3, 3) + ai_draft_bonus
    scores = scoring.deploy_fortify_territory_scoring(board)

    # Places all the troops in the highest scoring territory
    board.armies[scores.argmax()] += deploying

def fortify(board: gameboard.GameBoard, player) -> None:
    scores: npt.NDArray[np.floating] = scoring.deploy_fortify_territory_scoring(board)

    # choose the ending territory to be the one with the highest score
    end: int = int((scores * board.owners).argmax())

    # find all territories connected to the end territory
    owned = board.owners if player else ~board.owners
    connections: npt.NDArray[np.bool] = territory.total_connections(end, owned)

    if not np.any(connections):
        return

    # move troops from the worst remaining territory
    start: int = int((scores)[connections].argmin())
    board.fortify(start, end, int((scores.max() - scores.min()) * board.armies[start]))

def battle_wrapper(board: gameboard.GameBoard, start: int, end: int, attacking: int) -> gameboard.GameBoard:
    new_board = board.copy()
    new_board.battle(start, end, attacking)
    return new_board

def best_attack(board: gameboard.GameBoard, player: bool):
    owned = board.owners if player else ~board.owners

    # store the best move using the score and the resulting board
    best_move = (0, board)

    # since this attacks 1 territory at a time, just keep going until it runs out
    while True:
        prev_best_score = best_move[0]
        possible_attacks = np.array(np.nonzero(territory.adjMatrix & ~(best_move[1].owners))).T
        for start, end in possible_attacks:
            if board.armies[start] <= board.armies[end]:
                continue
            new_board = battle_wrapper(board, start, end, board.armies[start] - 1)
            new_score = scoring.score_board(new_board)
            if new_score > best_move[0]:
                best_move = (new_score, new_board)
        if prev_best_score == best_move[0]:
            break
    return best_move

def attack(board: gameboard.GameBoard, player):
    best_score, best_board = best_attack(board, player)
    board.owners = best_board.owners
    board.armies = best_board.armies

# basically this project is on par to be so goated and they will finish this project tonight and it is so easy to finish this project bc everyone is so locked in and this is so easy to code and print hello world and this is so much fun and this is so so so so so so so good and great because JCN is working on this so diligently
# by Shaurya