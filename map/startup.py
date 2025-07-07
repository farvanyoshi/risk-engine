import random
import sys
import territory

global players

def draft():
    pass # TODO

def attack(curr_player, attacking_territory_index, defending_territory_index, attacking_troop_amount):
    if check_adjacency(attacking_territory_index, defending_territory_index) and (attacking_troop_amount < territory.troops[attacking_troop_amount]) and : 


def check_adjacency(start_territory_index, end_territory_index):
    return territory.adjMatrix[start_territory_index] & (1 << (42 - end_territory_index))









if __name__ == '__main__':    
    assigner = list(range(42))
    random.shuffle(assigner)
    c = 0
    for i in assigner:
        territory.owner[c] = i % 2
        c += 1

    draft(territory.owner[0])