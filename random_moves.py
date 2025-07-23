import gameboard
import random
import numpy as np
import numpy.typing as npt
import territory
import interface.gui

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

def deploy(board: gameboard.GameBoard) -> None:
    deployed: int = max(int(np.count_nonzero(board.owners == board.is_player)) // 3, 3) + territory.continent_bonus(board.is_player, board.owners)
    print(f"The AI has {deployed} troops to deploy")
    while deployed > 0:
        placing: int = random.randrange(1, deployed + 1)
        location: int = random.choice(np.flatnonzero(~board.owners))
        board.armies[location] += placing
        deployed -= placing
        print(f"Deployed {placing} troops to {territory.territory_names[location].title()}")
    interface.gui.update_region()
def attack(board: gameboard.GameBoard) -> None:
    '''
    Pick only 1 random owned territory
    Check attackable territories
    Pick an attackable territory
    Choose a random number of troops to attack
    '''

    # randomly choose territories to attack from
    sampler: npt.NDArray[np.integer] = np.flatnonzero(~board.owners)
    np.random.shuffle(sampler)

    # if a possible attack is winnable, do it
    
    for start in sampler:
        attackable = np.flatnonzero(territory.adjMatrix[start] & board.owners)
        if len(attackable) > 0:
            end = np.random.choice(attackable)
            if board.armies[start] - 1 > board.armies[end]:
                attacking_troops = random.randrange(int(board.armies[end]) + 1, int(board.armies[start]))
                board.battle(start, end, attacking_troops)
                print(f"Attacked {np.char.title(territory.territory_names[end])} from {np.char.title(territory.territory_names[start])} with {attacking_troops} troops")
                break
    interface.gui.update_region()

def fortify(board: gameboard.GameBoard) -> None:
    start: int = np.random.choice(np.flatnonzero(~board.owners & (board.armies > 1)))
    connections: npt.NDArray[np.bool] = territory.total_connections(start, board.owners, False)
    while np.all(connections == 0):
        start = np.random.choice(np.flatnonzero(~board.owners))
        connections = territory.total_connections(start, board.owners, False)
    
    end: int = np.random.choice(np.flatnonzero(connections))
    num_troops: int = random.randrange(1, int(board.armies[start]))
    board.fortify(start, end, num_troops)
    print(f"Fortified {territory.territory_names[end].title()} from {territory.territory_names[start].title()} with {num_troops} troops")
    interface.gui.update_region()