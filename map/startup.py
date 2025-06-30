import sys
import json
import random
from territory import Territory

# open JSON map and load into territories dictionary
def load_map(filename):
    with open(filename) as f:
        raw_data = json.load(f)
    
    territories = []
    for name, data in raw_data.items():
        territories.append(Territory(name, data['continent'], data['adjacent']))

    return territories

def start(players, map):
    while players < 2 or players > 5:
        input("2-5 players please.")
    
    # Load up map and assign territories
    territories = load_map(map)
    assigner = list(range(42))
    random.shuffle(assigner)
    owned = [[] for i in range(players)]
    c = 0
    for i in assigner:
        territories[i].owner = c % players + 1
        owned[c % players].append(i)
        c += 1
    
    print(owned)
    for player_territories in owned:
        troops_per_player = [21, 14, 10, 8][players - 2]
        while troops_per_player > 0:
            x = random.choice(player_territories)
            territories[x].troops += 1
            troops_per_player -= 1
    for territory in territories:
        print(f"{territory.name} is owned by {territory.owner} with {territory.troops}")

if __name__ == "__main__":
    players = 2
    # players = int(input("How many players? (2-5 players): "))
    # Start game and send map file to game
    if len(sys.argv) > 1:
        start(players, sys.argv[1])
    start(players, "map/world_map.json")