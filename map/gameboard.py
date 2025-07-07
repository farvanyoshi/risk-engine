import random
from map.main import continentor, binator
import territory
class GameBoard:
    def __init__():
        troops = [1, 2, 3] * 14
        troops.shuffle()
        owners = [0, 1] * 21
        random.shuffle(owners)
        print(owners)

        cards = [0, 0]

    def move(player):
        GameBoard.deploy(player, GameBoard.owned.count(player) // 3 + continentor(player))
        
    def deploy(player, troops):
        if player == 1:
            while troops:
                territory = input(f"You have {troops} troops. Where are you deploying?")
                territory.owned(territory, player)
        

    def attack(player, start, end)