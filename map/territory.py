# Defines each node on the graph
class Territory:
    def __init__(self, name, continent, adj):
        self.name = name
        self.continent = continent
        self.adj = adj
        self.owner = 0
        self.troops = 1

    # Changes owner, which also requires changing troops
    def ownerize(self, owner, troops):
        self.owner = owner
        self.troops = troops
