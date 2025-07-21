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

def draft(board: gameboard.GameBoard) -> None:
    drafted: int = max(int(np.count_nonzero(board.owners == board.is_player) // 3), 3) + territory.continent_bonus(board.is_player, board.owners)
    while drafted > 0:
        placing: int = random.randrange(drafted)
        location: int = random.choice(np.flatnonzero(~board.owners))
        board.armies[location] += placing
        drafted -= placing

def attack(board: gameboard.GameBoard) -> None:
    '''
    Pick only 1 random owned territory
    Check attackable territories
    Pick an attackable territory
    Choose a random number of troops to attack
    '''
 
    # choose territory
    start: int = random.choice(np.flatnonzero(~board.owners))

    # search through all adjacent attackable territories
    attackables: npt.NDArray[np.bool] = territory.adjMatrix & (board.owners if board.is_player else ~board.owners)

    # randomly choose territories to attack from
    sampler: list[int] = random.sample(range(len(attackables)), len(attackables))

    # if a possible attack is winnable, do it
    # TODO: Refactor into one loop
    for i in sampler:

        # check if any territories are attackables
        if not np.any(attackables[i]):
            continue

        # Find the index of all attackable territories within that range and attack if able to
        attacked = False
        for j in np.flatnonzero(attackables[i]):
            if attacked: break
            if board.armies[i] > board.armies[j] + 1:
                board.battle(i, j, random.randrange(int(board.armies[j]) + 1, int(board.armies[i])))
                attacked = True
                break


            
    
    


def fortify(board: gameboard.GameBoard) -> None:
    pass