import cards
import gameboard
import numpy as np
import numpy.typing as npt
import scoring
import territory

DEPTH = 1
MAX_ATTACKS_PER_TURN = 42

def deploy(board: gameboard.GameBoard, player: int) -> None:
    place_troops(board, player, board.deploy_count(player) + trade_cards(board, player))

# Trades the best set of cards, but only while forced to: set values go up for everyone,
# so trading early mostly helps the other players (this tested better than trading every set)
def trade_cards(board: gameboard.GameBoard, player: int, forced_only: bool = True) -> int:
    troops: int = 0
    while not forced_only or board.must_trade(player):
        best: list[int] | None = cards.best_set(board.hands[player], board.owned(player))
        if best is None:
            break
        gained, bonus = board.trade(player, best)
        troops += gained
        print(cards.trade_message(gameboard.PLAYER_COLORS[player], best, gained, bonus))
    return troops

# Places all the troops in the highest scoring territory the player owns
def place_troops(board: gameboard.GameBoard, player: int, troops: int) -> None:
    if troops <= 0:
        return
    scores: npt.NDArray[np.floating] = scoring.deploy_fortify_territory_scoring(board, player)
    location: int = int(scores.argmax())
    board.armies[location] += troops
    print(f"{gameboard.PLAYER_COLORS[player]} deployed {troops} troops to {territory.territory_names[location].title()}")

def attack(board: gameboard.GameBoard, player: int, depth: int = DEPTH) -> None:
    # keep making the best attack until no attack improves the board
    for _ in range(MAX_ATTACKS_PER_TURN):
        if board.is_won():
            return
        current_score: float = scoring.score_board(board, player)
        best_score, best_move = minimax_attack(board, player, depth)
        if best_move is None or best_score <= current_score:
            return

        start, end, attacking_troops = best_move
        board.battle(start, end, attacking_troops)
        print(f"{gameboard.PLAYER_COLORS[player]} attacked {territory.territory_names[end].title()} from {territory.territory_names[start].title()} with {attacking_troops} troops")

        # taking an eliminated player's cards can force a trade, and those troops are placed right away
        if board.must_trade(player, cards.ELIMINATION_TRADE_HAND):
            place_troops(board, player, trade_cards(board, player))

# Every attack that captures a territory, either sending all but one troop,
# or sending only enough that the territory left behind can't be captured by its other enemy neighbors
def all_attacks(board: gameboard.GameBoard, player: int) -> list[tuple[int, int, int]]:
    owned = board.owned(player)
    moves: list[tuple[int, int, int]] = []
    for start in np.flatnonzero(owned & (board.armies > 1)):
        all_in = int(board.armies[start] - 1)
        enemy_neighbors = np.flatnonzero(territory.adjMatrix[start] & ~owned)
        for end in enemy_neighbors:
            other_enemies = board.armies[enemy_neighbors[enemy_neighbors != end]]
            keep = max(int(other_enemies.max()) - 1 if other_enemies.size else 1, 1)
            for attacking_troops in {all_in, int(board.armies[start]) - keep}:
                if attacking_troops > board.armies[end] and attacking_troops >= 1:
                    moves.append((int(start), int(end), attacking_troops))
    return moves

# Looks `depth` attacks ahead and returns the best reachable score with the first attack to get there
def minimax_attack(board: gameboard.GameBoard, player: int, depth: int) -> tuple[float, tuple[int, int, int] | None]:
    if depth == 0 or board.is_won():
        return scoring.score_board(board, player), None

    best_score: float = -np.inf
    best_move: tuple[int, int, int] | None = None

    for move in all_attacks(board, player):
        new_board = board.copy()
        new_board.battle(*move)
        score, _ = minimax_attack(new_board, player, depth - 1)
        if score > best_score:
            best_score = score
            best_move = move

    return best_score, best_move

def fortify(board: gameboard.GameBoard, player: int) -> None:
    owned = board.owned(player)
    scores: npt.NDArray[np.floating] = scoring.deploy_fortify_territory_scoring(board, player)

    # choose the ending territory to be the one with the highest score
    end: int = int(scores.argmax())

    # find all territories connected to the end territory that can give troops
    connections: npt.NDArray[np.bool] = territory.total_connections(end, owned) & (board.armies > 1)
    if not np.any(connections):
        return

    # move troops from the worst connected territory, leaving one behind
    candidates: npt.NDArray[np.integer] = np.flatnonzero(connections)
    start: int = int(candidates[scores[candidates].argmin()])
    transferring: int = int(board.armies[start] - 1)
    board.fortify(start, end, transferring)
    print(f"{gameboard.PLAYER_COLORS[player]} fortified {territory.territory_names[end].title()} from {territory.territory_names[start].title()} with {transferring} troops")


# basically this project is on par to be so goated and they will finish this project tonight and it is so easy to finish this project bc everyone is so locked in and this is so easy to code and print hello world and this is so much fun and this is so so so so so so so good and great because JCN is working on this so diligently
# by Shaurya
