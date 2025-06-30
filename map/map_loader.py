import json
from territory import Territory

def load_map(filename):
    with open(filename) as f:
        raw_data = json.load(f)
    
    territories = {}
    for name, data in raw_data.items():
        territories[name] = Territory(data['continent'], data['adjacent'])
    
    return territories


load_map("map/world_map.json")