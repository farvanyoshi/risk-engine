import random
import sys
from territory import *

global players

def continents(player):
    pass

def draft(player):
    drafted = owned.count(player) // 3 + continents(player)
    

def attack(curr_player, attacking_territory_index, defending_territory_index, attacking_troop_amount):
    if check_adjacency(attacking_territory_index, defending_territory_index) and (attacking_troop_amount < territory.troops[attacking_troop_amount]) and : 


def check_adjacency(start_territory_index, end_territory_index):
    return territory.adjMatrix[start_territory_index] & (1 << (42 - end_territory_index))






if __name__ == '__main__':
    print(owned)
    draft(owned[0])