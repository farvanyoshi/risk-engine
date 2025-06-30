from startup import players

# TODO: Create player object
class Player:
    def __init__(self, cards):
        self.cards = cards

player_turn = "player1"
endturn = False

player_list = ["player1", "player2", "player3", "player4","player5"][0:players-1] #need to bring this from startup.py

def change_player_turn():
    #Iterates to the next player's 
    end = input("end turn?(y/n)")
    if end == "y":
        endturn = True
    for i in player_list:
        if endturn == True:
            endturn == False
            if player_turn != "player5":
                player_turn == player_list[i+1]
            elif player_turn == "player5":
                player_turn = "player1"

def game_state():
    while True:
        
        change_player_turn()

        if game_check():
            break

def game_check(): 0