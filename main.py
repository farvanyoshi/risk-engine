import random
from gameboard import GameBoard
from territory import *

# def attack(curr_player, attacking_territory_index, defending_territory_index, attacking_troop_amount):
    # if check_adjacency(attacking_territory_index, defending_territory_index) and (attacking_troop_amount < troops[attacking_troop_amount]) and : 

if __name__ == '__main__':
    game = GameBoard()
    game.move(round(random.random()))