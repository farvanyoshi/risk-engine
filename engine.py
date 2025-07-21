import gameboard
import numpy as np
import territory

def deploy(board: gameboard.GameBoard) -> None:
    ai_draft_bonus: int = territory.continent_bonus(False, board.owners)
    deployed: int = max(int(np.count_nonzero(board.owners == board.is_player)) // 3, 3) + ai_draft_bonus
    
    ''' trying out code
    need a way to count all the enemy troops around a territory
    '''
    player_adjacency = territory.adjMatrix & board.owners