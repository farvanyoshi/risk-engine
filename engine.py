import numpy as np
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

def draft(board) -> None:
    random.choice()