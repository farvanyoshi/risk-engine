# Defines each node on the graph
class Territory:
    def __init__(self, continent, adj):
        self.continent = continent
        self.adj = adj
        self.owner = None
        self.troops = 0

    # Changes owner, which also requires changing troops
    def ownerize(self, owner, troops):
        self.owner = owner
        self.troops = troops
