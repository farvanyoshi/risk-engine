import cards
import gameboard
import random
import numpy as np
import numpy.typing as npt
import territory

'''
Steps:
- Implement the draft phase (assume best places to place territories are those)
    - Calculate threat from all neighboring enemy troops
    - Divide by number of troops in the territory to get threat ratio
    - Normalize ratio and add troops to greatest value
- Implement the attack phase
- Implement the fortify phase

- Create a "best move" function that connects these phases together off of a heuristic scoring function
- Use a scoring function to determine the value of every move
    - territories gained
    - troops left
    - number of unique borders, number of isolated territories (or level of interconnectedness)

- To simplify the scoring function, the ai's draft and attack phase can be turned into one
    - assign every bordering territory all the draft troops, and find how to reach the most score
'''

# After each attack, the chance of stopping the attack phase
STOP_CHANCE = 0.1
MAX_ATTACKS_PER_TURN = 42

def deploy(board: gameboard.GameBoard, player: int) -> None:
    place_troops(board, player, board.deploy_count(player) + trade_cards(board, player))

# Only trades when forced to, picking any valid set. Returns the troops gained
def trade_cards(board: gameboard.GameBoard, player: int) -> int:
    troops: int = 0
    while board.must_trade(player):
        traded: list[int] = random.choice(cards.all_sets(board.hands[player]))
        gained, bonus = board.trade(player, traded)
        troops += gained
        print(cards.trade_message(gameboard.PLAYER_COLORS[player], traded, gained, bonus))
    return troops

# Puts all the troops on one random territory that borders an enemy, so they can be used to attack
def place_troops(board: gameboard.GameBoard, player: int, deployed: int) -> None:
    if deployed <= 0:
        return
    owned = board.owned(player)
    border = np.flatnonzero(owned & (territory.adjMatrix & ~owned).any(1))
    location: int = int(random.choice(border if border.size else np.flatnonzero(owned)))
    board.armies[location] += deployed
    print(f"{gameboard.PLAYER_COLORS[player]} deployed {deployed} troops to {territory.territory_names[location].title()}")

# Keeps making random attacks it can win, stopping at random or when there are none left
def attack(board: gameboard.GameBoard, player: int) -> None:
    for _ in range(MAX_ATTACKS_PER_TURN):
        if board.is_won() or not random_attack(board, player) or random.random() < STOP_CHANCE:
            return

def random_attack(board: gameboard.GameBoard, player: int) -> bool:
    '''
    Pick random owned territories
    Check attackable territories
    Pick an attackable territory
    Choose a random number of troops to attack
    Returns whether an attack was made
    '''

    owned = board.owned(player)

    # randomly choose territories to attack from
    sampler: npt.NDArray[np.integer] = np.flatnonzero(owned)
    np.random.shuffle(sampler)

    # if a possible attack is winnable, do it
    for start in sampler:
        attackable = np.flatnonzero(territory.adjMatrix[start] & ~owned)
        if len(attackable) > 0:
            end = np.random.choice(attackable)
            if board.armies[start] - 1 > board.armies[end]:
                attacking_troops = random.randrange(int(board.armies[end]) + 1, int(board.armies[start]))
                board.battle(start, end, attacking_troops)
                print(f"{gameboard.PLAYER_COLORS[player]} attacked {territory.territory_names[end].title()} from {territory.territory_names[start].title()} with {attacking_troops} troops")

                # taking an eliminated player's cards can force a trade, and those troops are placed right away
                if board.must_trade(player, cards.ELIMINATION_TRADE_HAND):
                    place_troops(board, player, trade_cards(board, player))
                return True
    return False
    
def fortify(board: gameboard.GameBoard, player: int) -> None:
    owned = board.owned(player)
    possible_starts = np.flatnonzero(owned & (board.armies > 1))
    if possible_starts.size == 0:
        return
    start: int = int(np.random.choice(possible_starts))
    connections: npt.NDArray[np.bool] = territory.total_connections(start, owned)
    if not np.any(connections):
        return

    end: int = np.random.choice(np.flatnonzero(connections))
    num_troops: int = random.randrange(1, int(board.armies[start]))
    board.fortify(start, end, num_troops)
    print(f"{gameboard.PLAYER_COLORS[player]} fortified {territory.territory_names[end].title()} from {territory.territory_names[start].title()} with {num_troops} troops")
