import json


def sort_territories(json_data):
    # Parse JSON string if input is a string
    if isinstance(json_data, str):
        data = json.loads(json_data)
    else:
        data = json_data
    
    # Sort the dictionary by territory names (keys)
    sorted_data = dict(sorted(data.items(), key=lambda x: x[0]))
    
    # Ensure adjacent territories are also sorted alphabetically
    for territory in sorted_data:
        sorted_data[territory]['adjacent'] = sorted(sorted_data[territory]['adjacent'])
    
    return sorted_data

# Example usage
if __name__ == "__main__":
    territories = json.load("map/world_map.json")
    
    sorted_territories = sort_territories(territories)
    
    # Print the sorted data
    print(json.dumps(sorted_territories, indent=2))