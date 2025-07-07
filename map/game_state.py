from startup import players

# TODO: Create player object 

player_1_territories = []
player_2_territories = []

player_turn = "player1"

player_list = list(players) #need to bring this from startup.py

def change_player_turn():
    #Iterates to the next player's 
    end = input("end turn?(y/n)")
    

def game_state():
    while True:
        
        change_player_turn()

        if game_check():
            break

def game_check(): 0

#this probably won't stay here but like a terminal thingy
def choose_territory(player):
    territory = input("What territory: ")
    return territory

def draft(player, territoriesa, continents_owned):
    territory = choose_territory(player)
    

    

def fortify(player, receiving_territory, delivering_territory, amount):
    if receiving_territory.get_owner() & delivering_territory.get_owner() & delivering_territory.get_troops() > 1 & amount <= delivering_territory - 1:
        receiving_territory += amount
        delivering_territory -= amount
        return 0
    else:
        return -1
        

def transfer_territory(winner_player, loser_player, territory):
    pass