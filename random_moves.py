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

def deploy(board: gameboard.GameBoard, player: int) -> None:
    owned = board.owned(player)
    deployed: int = board.deploy_count(player)
    while deployed > 0:
        placing: int = random.randrange(1, deployed + 1)
        location: int = random.choice(np.flatnonzero(owned)) # np.flatnonzero(owned) finds the indices of all territories owned by this player
        board.armies[location] += placing
        deployed -= placing
        print(f"{gameboard.PLAYER_COLORS[player]} deployed {placing} troops to {territory.territory_names[location].title()}")

def attack(board: gameboard.GameBoard, player: int) -> None:
    '''
    Pick only 1 random owned territory
    Check attackable territories
    Pick an attackable territory
    Choose a random number of troops to attack
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
                break
    
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
