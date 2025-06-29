class Territory:
    def __init__(self, name, continent, adjacency):
        self.name = name
        self.continent = continent
        self.adjacency = adjacency
        self.owner = None
        self.troops = 0

    def ownerize(self, owner, troops):
        self.owner = owner
        self.troopify(troops)

    def troopify(self, troops):
        self.troops = troops

    def get_neighbors(self):
        return self.neighbors
    
    def get_troops(self):
        return self.troops
    
    def get_owner(self):
        return self.owner

raw_data = '''
    # North America
    Alaska -- {Kamchatka Northwest Alberta}
    Northwest -- {Greenland Ontario Alberta}
    Greenland -- {Ontario Quebec Iceland}
    Alberta -- {Ontario WUS}
    Ontario -- {Quebec WUS EUS}
    Quebec -- EUS
    WUS -- {EUS CAm}
    EUS -- CAm
    CAm -- Venezuela

    # South America
    Venezuela -- {Brazil Peru}
    Peru -- {Brazil Argentina}
    Brazil -- {NAf Argentina}

    # Europe
    Iceland -- {Scandinavia GBr}
    Scandinavia -- {GBr NEu Ukraine}
    GBr -- {NEu WEu}
    NEu -- {WEu SEu Ukraine}
    Ukraine -- {Ural Afghanistan MEu SEu}
    WEu -- {SEu NAf}
    SEu -- {MEu Egypt NAf}
    
    # Africa
    NAf -- {Egypt EAf Congo}
    Egypt -- {MEu EAf}
    EAf -- {MEu Congo SAf Madagascar}
    Congo -- SAf
    SAf -- Madagascar

    # Asia
    Ural -- {Siberia China Afghanistan}
    Siberia -- {Yakutsk Irkutsk Mongolia China}
    Yakutsk -- {Kamchatka Irkutsk}
    Mongolia -- {Japan China}
    Japan -- Kamchatka
    Afghanistan -- {China India MEu}
    China -- {Siam India}
    MEu -- India
    India -- Siam
    Siam -- Indonesia

    # Oceania
    Indonesia -- {NGu WAu}
    NGu -- {WAu EAu}
    WAu -- EAu
'''

territories = {}
current_continent = None

for line in raw_data.strip().splitlines():
    line = line.strip()
    if line.startswith('#'):
        current_continent = line[1:].strip()
    elif '--' in line:
        name, neighbors = line.split('--')
        name = name.strip()
        neighbors = neighbors.strip().strip('{}').split()
        territory = Territory(name=name, continent=current_continent, adjacency=neighbors)
        territories[name] = territory

