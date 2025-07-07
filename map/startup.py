import random
import sys
from territory import *

global players

def continents(player):
    pass

def draft(curr_player):
    drafted = owner.count(curr_player) // 3 + continents(curr_player)

 

def attack(curr_player, attacking_territory_index, defending_territory_index, attacking_troop_amount):
    if check_adjacency(attacking_territory_index, defending_territory_index) and (attacking_troop_amount < troops[attacking_troop_amount]) and (owned[attacking_territory_index] == curr_player) and (owner[defending_territory_index] != curr_player): 
        if attacking_troop_amount > troops[defending_territory_index]:
            troops[defending_territory_index] = -(troops[defending_territory_index]-attacking_troop_amount)
            owned[defending_territory_index] = curr_player
        elif attacking_troop_amount == troops[defending_territory_index]:
            troops[defending_territory_index] = 1
        else:
            troops[defending_territory_index] -= attacking_troop_amount
        troops[attacking_territory_index] -= attacking_troop_amount

    else:
        #Tell that its invalid
        #get the values 
        attack(curr_player, , , ) #returns the whole thing


# Nirvan got this
def check_adjacency(start_territory_index, end_territory_index):
    return adjMatrix[start_territory_index] & (1 << (42 - end_territory_index))






if __name__ == '__main__':
    print(owned)
    draft(owned[0])