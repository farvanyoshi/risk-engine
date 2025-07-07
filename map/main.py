import random
from gameboard import GameBoard
from territory import *

global game

def continentor(player):
    owned_string = binator(game.owned)
    player_bonus = 0
    if not player:
        owned_string = ~owned_string
    for continent, bonus in zip(continents, continent_bonuses):
        if owned_string & continent == continent:
            player_bonus += bonus
    return bonus

def binator(mat):
            new = 0
            for i in range(len(game.owned)):
                new += (game.owned[i] << (42 - i))
            return new    

# def attack(curr_player, attacking_territory_index, defending_territory_index, attacking_troop_amount):
    # if check_adjacency(attacking_territory_index, defending_territory_index) and (attacking_troop_amount < troops[attacking_troop_amount]) and : 


def check_adjacency(start_territory_index, end_territory_index):
    return adjMatrix[start_territory_index] & (1 << (42 - end_territory_index))

if __name__ == '__main__':
    game = GameBoard()
    game.move(round(random.random()))