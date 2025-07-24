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

def all_attacks_generator(state: gameboard.GameBoard, player: bool):
    new_states = []
    for start in np.flatnonzero(state.owners == player):
        if state.armies[start] <= 1:
            continue
        # Find adjacent enemies
        neighbors = np.flatnonzero(territory.adjMatrix[start] & (state.owners != player))
        for end in neighbors:
            # Simulate winning the attack: take territory with 1 army
            new_board = state.copy()
            new_board.owners[end] = player
            new_board.armies[start] -= 1  # leave one behind
            new_board.armies[end] = 1     # place one in captured territory
            new_states.append(new_board)

    return new_states

def attack(board: gameboard.GameBoard, player):
    _, best_board = minimax(board, 1, player)
    np.copyto(board.owners, best_board.owners)
    np.copyto(board.armies, best_board.armies)

def minimax(board: gameboard.GameBoard, depth: int, player: bool, visited = None):
    if depth == 0:
        return scoring.score_board(board), board
    
    if visited is None:
        visited = set()

    new_board = board.copy()
    deploy(board.copy(), player)

    best_score = -np.inf
    best_state = new_board

    queue = [new_board]
    visited.add(new_board.hash())

    while queue:
        current = queue.pop()
        next_states = all_attacks_generator(current, player)

        for state in next_states:
            key = board.hash()
            if key in visited:
                continue
            visited.add(key)

            final_state = state.copy()
            fortify(final_state, player)

            score, _ = minimax(final_state, depth - 1, not player, visited)
            if score > best_score:
                best_score = score
                best_state = state

            queue.append(state)  # Continue BFS from this state

    return best_score, best_state
    # implement a single attack and repeat attacking until no longer possible, then recurse
    # TODO: Implement recursion through the minimax tree

# basically this project is on par to be so goated and they will finish this project tonight and it is so easy to finish this project bc everyone is so locked in and this is so easy to code and print hello world and this is so much fun and this is so so so so so so so good and great because JCN is working on this so diligently
# by Shaurya