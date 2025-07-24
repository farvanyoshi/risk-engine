import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk
import cv2
import numpy as np
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from gameboard import GameBoard
import territory

import sys
import os

import random_moves


region_to_name = {
        113: "Afghanistan",
        163: "Alaska",
        140: "Alberta",
        25: "Argentina",
        56: "Brazil",
        86: "Central America",
        107: "China",
        29: "Congo",
        49: "East Africa",
        21: "Eastern Australia",
        112: "Eastern United States",
        61: "Egypt",
        127: "Great Britain",
        130: "Great Britain",
        177: "Greenland",
        145: "Iceland",
        83: "India",
        28: "Indonesia",
        36: "Indonesia",
        27: "Indonesia",
        17: "Indonesia",
        20: "Indonesia",
        144: "Irkutsk",
        120: "Japan",
        168: "Kamchatka",
        9: "Madagascar",
        78: "Middle East",
        118: "Mongolia",
        43: "New Guinea",
        44: "New Guinea",
        67: "North Africa",
        122: "Northern Europe",
        169: "Northwest Territory",
        139: "Ontario",
        54: "Peru",
        143: "Quebec",
        160: "Russia",
        161: "Scandinavia",
        69: "Siam",
        175: "Siberia",
        15: "South Africa",
        94: "Southern Europe",
        167: "Ural",
        64: "Venezuela",
        14: "Western Australia",
        95: "Western Europe",
        114: "Western United States",
        172: "Yakutsk"
    }

name_to_region = {
    "afghanistan": 113,
    "alaska": 163,
    "alberta": 140,
    "argentina": 25,
    "brazil": 56,
    "central america": 86,
    "china": 107,
    "congo": 29,
    "east africa": 49,
    "eastern australia": 21,
    "eastern united states": 112,
    "egypt": 61,
    "great britain": 127,
    "greenland": 177,
    "iceland": 145,
    "india": 83,
    "indonesia": 28,
    "irkutsk": 144,
    "japan": 120,
    "kamchatka": 168,
    "madagascar": 9,
    "middle east": 78,
    "mongolia": 118,
    "new guinea": 43,
    "north africa": 67,
    "northern europe": 122,
    "northwest territory": 169,
    "ontario": 139,
    "peru": 54,
    "quebec": 143,
    "russia": 160,
    "scandinavia": 161,
    "siam": 69,
    "siberia": 175,
    "south africa": 15,
    "southern europe": 94,
    "ural": 167,
    "venezuela": 64,
    "western australia": 14,
    "western europe": 95,
    "western united states": 114,
    "yakutsk": 172
}



def validate_int_input(new_value):
    if new_value == "" or new_value.isdigit():
        return True
    return False

game: GameBoard = GameBoard()

def loop_game_stage():
    global game_phase, available_deployable_troops
    if game_phase == "Deploy":
        enable_button(confirm_action_button)
        enable_button(next_stage_button)
        set_next_stage_button("Skip Stage")
        disable_available_troops_label()
        game_phase = "Attack"
    elif game_phase == "Attack":
        set_next_stage_button("Skip Stage")
        game_phase = "Fortify"
    elif game_phase == "Fortify":
        ai_play()
        set_next_stage_button("Next Stage")
        game_phase = "Deploy"
        disable_button(next_stage_button)
        available_deployable_troops = calculate_deploy_troop_amount()
        update_available_troops_label()
        
        

    enable_button(confirm_action_button) 
    clear_territories()

    update_phase_label()
    output_message(game_phase)


def ai_play():
    random_moves.deploy(game)
    random_moves.attack(game)
    random_moves.fortify(game)

    


def next_stage():
    loop_game_stage()

def confirm_action():
    input_action()

def calculate_deploy_troop_amount() -> int:
    return max(int(np.count_nonzero(game.owners == game.is_player)) // 3, 3) + territory.continent_bonus(game.is_player, game.owners)


def input_action():
    global game_phase, first_touch, Even_click, click_idx

    if game.is_won():
        # Could disable the button for next turn
        print("Game over!")
        return

    print(f"It is now the {'player' if game.is_player else 'AI'}'s turn")

    print(game.owners)

    match game_phase:
        case "Deploy":
            location: str = start_terr_name.lower()
            
            i: int = territory.indexer(location)

            global troop_amount_selection, available_deployable_troops

            output_message(str(game.owners[i]))
            output_message(str(i))
            output_message(str(start_terr_name))

            if game.owners[i] and troop_amount_selection > 0 and (troop_amount_selection <= available_deployable_troops) and location != "" and game.owners[i]:
                output_message("It works")
                game.armies[i] += troop_amount_selection
                print(f"{troop_amount_selection} troops added to {location.title()}.")
                available_deployable_troops -= troop_amount_selection
                update_available_troops_label()
                if available_deployable_troops == 0:
                    enable_button(next_stage_button)
                    disable_button(confirm_action_button)
                    clear_territories()
                    first_touch = None
                    Even_click = True
                    click_idx = 0
                update_phase_label()
                    
            else: 
                output_message("Invalid")

            
    
        case "Attack":
            start_index: int = territory.indexer(start_terr_name.lower())
            end_index: int = territory.indexer(end_terr_name.lower())

            output_message(str(start_index))
            output_message(" ")
            output_message(str(end_index))

            possible_targets: np.ndarray = territory.adjMatrix[start_index] & ~game.owners


            if  (0 < troop_amount_selection and troop_amount_selection < game.armies[start_index]) and (start_index != -1) and (end_index != -1) and possible_targets[end_index] and game.owners[start_index] and not game.owners[end_index] and not np.all(possible_targets == 0):
                game.battle(start_index, end_index, troop_amount_selection)
                output_message(f"Attacked {end_terr_name.title()} from {start_terr_name.title()} with {troop_amount_selection} troops")
                set_next_stage_button("Next Stage")
                output_message("Attack Done!")
                clear_territories()

                first_touch = None
                Even_click = True
                click_idx = 0
            else: 
            
                output_message("Invalid")
        case "Fortify":
            start_index = territory.indexer(start_terr_name.lower())
            end_index = territory.indexer(end_terr_name.lower())

            connection_matrix = territory.total_connections(start_index, game.owners, True)
            connections = {
                territory.territory_names[index].lower()
                for index, connected in enumerate(connection_matrix)
                if connected
            }

            max_troops = game.armies[start_index] - 1

            output_message(str(max_troops))

            output_message(f"Connections: {connections}")
            output_message(" ")
            output_message(f"{end_terr_name.lower()} in connections? {end_terr_name.lower() in connections}")
            output_message(" ")
            output_message(f"Troop amount <= max? {troop_amount_selection <= max_troops}")

            if end_terr_name.lower() in connections and troop_amount_selection <= max_troops:
                game.fortify(start_index, end_index, troop_amount_selection)  # NOT max_troops
                output_message("Fortified!")
                set_next_stage_button("Next Stage")
                disable_button(confirm_action_button)
                clear_territories()
                first_touch = None
                Even_click = True
                click_idx = 0
            else:
                output_message("Invalid")
    # if game.is_player:
    #     # player.deploy(game)
    #     # player.attack(game)
    #     # player.fortify(game)
    #     game.is_player = False
    # else:
    #     pass
    #     # random_moves.deploy(game)
    #     # update_region(canvas, edges)
    #     # random_moves.attack(game)
    #     # update_region(canvas, edges)
    #     # random_moves.fortify(game)
    #     # update_region(canvas, edges)
    #     game.is_player = True
    # # root1.mainloop()

def on_click(event):
    # region_name = "Not a Region"
    clicked = True
    region_name = ""
    #print(f"Mouse clicked at {event.x}, {event.y}")
    for i, region in enumerate(regions):
        region_num = i+1
        if cv2.pointPolygonTest(region, (event.x, event.y), False) >= 0:
            print(f"Clicked inside region {region_num}")
            try:
                region_name = region_to_name[region_num]
                match game_phase:
                    case "Deploy":
                        deploy_region_input(region_name)
                    case "Attack":
                        attack_region_input(region_name)
                    case "Fortify":
                        fortify_region_input(region_name)
            except KeyError:
                pass
            if region_num != 170 and region_num != 176 and region_num != 74 and region_num != 76 and region_num !=85 and region_num != 96 and region_num != 59 and region_num != 63 and region_num != 37 and region_num != 136 and region_num != 133 and region_num != 152 and region_num != 155 and region_num != 91 and region_num != 117 and region_num != 138 and region_num != 111:
                update_region(canvas, edges, clicked, region_num)

    update_region(canvas, edges, clicked, "")


            
    

def deploy_region_input(name_of_region):
    global start_terr_name, end_terr_name
    if start_terr_name == "":
        start_terr_name = name_of_region
        enable_button(confirm_action_button)
    elif start_terr_name == name_of_region and end_terr_name == "":
        start_terr_name = ""
        disable_button(confirm_action_button)
    else:
        output_message("Invalid ")

    update_start_label()


def attack_region_input(name_of_region):
    global start_terr_name, end_terr_name
    if start_terr_name == "":
        start_terr_name = name_of_region
    elif start_terr_name == name_of_region and end_terr_name == "":
        start_terr_name = ""
    elif start_terr_name != "" and end_terr_name == "":
        end_terr_name = name_of_region
    elif start_terr_name != "" and end_terr_name == name_of_region:
        end_terr_name = ""
    else:
        output_message("Invalid ")
    
    update_start_label()
    update_end_label()
    



def fortify_region_input(name_of_region):
    global start_terr_name, end_terr_name
    if start_terr_name == "":
        start_terr_name = name_of_region
    elif start_terr_name == name_of_region and end_terr_name == "":
        start_terr_name = ""
    elif start_terr_name != "" and end_terr_name == "":
        end_terr_name = name_of_region
    elif start_terr_name != "" and end_terr_name == name_of_region:
        end_terr_name = ""
    else:
        output_message("Invalid ")

    update_start_label()
    update_end_label()

def click_contours(edges):
    global start_terr_name, end_terr_name, start_contour, end_contour

    output_message(start_terr_name)
    output_message(end_terr_name)

    labeled_img = np.ones((edges.shape[0], edges.shape[1], 3), dtype=np.uint8) * 255  # White background
    labeled_img[edges != 0] = (0, 0, 0)

    try: 
        start_region_num = name_to_region[start_terr_name]
        if start_region_num:
            start_contour = regions[start_region_num - 1]

        if start_region_num == 20 or start_region_num == 28 or start_region_num == 27 or start_region_num == 17 or start_region_num == 36:
            cv2.drawContours(labeled_img, [regions[27]], -1, (255, 0, 0), 10)
            cv2.drawContours(labeled_img, [regions[26]], -1, (255, 0, 0), 10)
            cv2.drawContours(labeled_img, [regions[16]], -1, (255, 0, 0), 10)
            cv2.drawContours(labeled_img, [regions[35]], -1, (255, 0, 0), 10)
        cv2.drawContours(labeled_img, [start_contour], -1, (255, 0, 0), 10)
        
        output_message(str(start_region_num))

        return labeled_img

    except KeyError:
        pass     

    try:
        end_region_num = name_to_region[end_terr_name]
        if end_region_num:
            end_contour = regions[end_region_num - 1]

        if start_region_num == 20 or start_region_num == 28 or start_region_num == 27 or start_region_num == 17 or start_region_num == 36:
            cv2.drawContours(labeled_img, [regions[27]], -1, (0, 255, 255), 10)
            cv2.drawContours(labeled_img, [regions[26]], -1, (0, 255, 255), 10)
            cv2.drawContours(labeled_img, [regions[16]], -1, (0, 255, 255), 10)
            cv2.drawContours(labeled_img, [regions[35]], -1, (0, 255, 255), 10)
        cv2.drawContours(labeled_img, [end_contour], -1, (0, 255, 255), 10)

        output_message(str(end_region_num))

        return labeled_img
    
    except KeyError:
        pass
    
    return


    
    

    

def singleclick(region_numb, region, edges):
    global first_touch
    global Even_click
    global click_idx
    labeled_img = np.ones((edges.shape[0], edges.shape[1], 3), dtype=np.uint8) * 255  # White background
    labeled_img[edges != 0] = (0, 0, 0)

    if region_numb == first_touch:
        first_touch = region_numb
        if Even_click == True:
            Even_click = False
            return labeled_img
        elif Even_click == False:
            Even_click = True
            if region_numb == 20 or region_numb == 28 or region_numb == 27 or region_numb ==17 or region_numb ==36:
                cv2.drawContours(labeled_img, [regions[27]], -1, (255, 0, 0), 10)
                cv2.drawContours(labeled_img, [regions[26]], -1, (255, 0, 0), 10)
                cv2.drawContours(labeled_img, [regions[16]], -1, (255, 0, 0), 10)
                cv2.drawContours(labeled_img, [regions[35]], -1, (255, 0, 0), 10)
            cv2.drawContours(labeled_img, [region], -1, (255, 0, 0), 10)
            first_touch = region_numb
            return labeled_img
    else:
        if region_numb != first_touch and Even_click == True and click_idx>0:
            return
        else:
            Even_click = True
            if region_numb == 20 or region_numb == 28 or region_numb == 27 or region_numb ==17 or region_numb ==36:
                cv2.drawContours(labeled_img, [regions[27]], -1, (255, 0, 0), 10)
                cv2.drawContours(labeled_img, [regions[26]], -1, (255, 0, 0), 10)
                cv2.drawContours(labeled_img, [regions[16]], -1, (255, 0, 0), 10)
                cv2.drawContours(labeled_img, [regions[35]], -1, (255, 0, 0), 10)
            cv2.drawContours(labeled_img, [region], -1, (255, 0, 0), 10)
            click_idx +=1
            first_touch = region_numb
            return labeled_img


def doubleclick(labeled_img, region_numb, region):
    global first_touch, even_click, click_idx

    if region_numb == first_touch:
        first_touch = region_numb
        if even_click == True:
            even_click = False
            return labeled_img
        elif even_click == False:
            even_click = True
            if region_numb == 20 or region_numb == 28 or region_numb == 27 or region_numb ==17 or region_numb ==36:
                cv2.drawContours(labeled_img, [regions[27]], -1, (255, 0, 0), 10)
                cv2.drawContours(labeled_img, [regions[26]], -1, (255, 0, 0), 10)
                cv2.drawContours(labeled_img, [regions[16]], -1, (255, 0, 0), 10)
                cv2.drawContours(labeled_img, [regions[35]], -1, (255, 0, 0), 10)
            cv2.drawContours(labeled_img, [region], -1, (255, 0, 0), 10)
            first_touch = region_numb
            return labeled_img
    else:
        if region_numb != first_touch and even_click == True and click_idx>0:
            if region_numb != first_touch and even_click == True and click_idx>0:
                first_touch_region = regions[first_touch -1]
                cv2.drawContours(labeled_img, [first_touch_region], -1, (255, 0, 0), 10)
                cv2.drawContours(labeled_img, [region], -1, (0, 255, 255), 10)
                return labeled_img
        else:
            even_click = True
            if region_numb == 20 or region_numb == 28 or region_numb == 27 or region_numb ==17 or region_numb ==36:
                cv2.drawContours(labeled_img, [regions[27]], -1, (255, 0, 0), 10)
                cv2.drawContours(labeled_img, [regions[26]], -1, (255, 0, 0), 10)
                cv2.drawContours(labeled_img, [regions[16]], -1, (255, 0, 0), 10)
                cv2.drawContours(labeled_img, [regions[35]], -1, (255, 0, 0), 10)
            cv2.drawContours(labeled_img, [region], -1, (255, 0, 0), 10)
            click_idx +=1
            first_touch = region_numb
            return labeled_img




# opens risk board image
def open_image(canvas, img_cv):

    
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)
    img_tk = ImageTk.PhotoImage(img_pil)

    canvas.configure(image=img_tk)
    canvas.image = img_tk


def update_region(canvas, edges, clicked, region_numb):

    #light background
    labeled_img = np.ones((edges.shape[0], edges.shape[1], 3), dtype=np.uint8) * 255  # White background
    labeled_img[edges != 0] = (0, 0, 0)
    
    global first_touch

    # if clicked == True:
    #     clicked = False
    #     region = regions[region_numb - 1]
    #     labeled_img = click_contours(edges)

    # if clicked == True:
    #     clicked = False
    #     region = regions[region_numb - 1]
    #     match game_phase:
    #         case "Deploy":
    #             labeled_img = singleclick(region_numb, region, edges)
    #         case "Attack":
    #             labeled_img = doubleclick(region_numb, region, edges)
    #         case "Fortify":
    #             labeled_img = doubleclick(region_numb, region, edges)
        
    




        
    # Functionality: labels 
    index = 0
    for region_num, region_name in region_to_name.items():
        if region_num == 27 or region_num == 17 or region_num == 20 or region_num ==36 or region_num ==43 or region_num == 130:
            continue

            # Skip if the region number is out of bounds
        if region_num - 1 < 0 or region_num - 1 >= len(regions):
            continue
        

        region = regions[region_num - 1]  # get the contour by index

        #colors for each region based on owner
        if game.owners[index] == True:
            if region_num == 28:
                #make whole indonesia one color
                cv2.drawContours(labeled_img, [regions[region_num - 1]], -1, (0,255,0), thickness=cv2.FILLED)
                cv2.drawContours(labeled_img, [regions[region_num - 2]], -1, (0,255,0), thickness=cv2.FILLED)
                cv2.drawContours(labeled_img, [regions[region_num + 7]], -1, (0,255,0), thickness=cv2.FILLED)
                cv2.drawContours(labeled_img, [regions[region_num - 12]], -1, (0,255,0), thickness=cv2.FILLED)

            cv2.drawContours(labeled_img, [region], -1, (0,255,0), thickness=cv2.FILLED)
        if game.owners[index]== False:
            if region_num ==28:
                cv2.drawContours(labeled_img, [regions[region_num - 1]], -1, (0,0,255), thickness=cv2.FILLED)
                cv2.drawContours(labeled_img, [regions[region_num - 2]], -1, (0,0,255), thickness=cv2.FILLED)
                cv2.drawContours(labeled_img, [regions[region_num + 7]], -1, (0,0,255), thickness=cv2.FILLED)
                cv2.drawContours(labeled_img, [regions[region_num - 12]], -1, (0,0,255), thickness=cv2.FILLED)
            cv2.drawContours(labeled_img, [region], -1, (0,0,255), thickness=cv2.FILLED)
    






        # Calculate center of the region using image moments
        M = cv2.moments(region)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])

            # Draw the name on the image
            cv2.putText(
                labeled_img,             # image you're writing on
                region_name,             # name to draw
                (cx-22, cy+5),                # location (center of region) shifted to center text
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,                     # font scale
                (0, 0, 0),             # black text
                1,                       # thickness
                cv2.LINE_AA              # anti-aliased
            )
            cv2.putText(
                labeled_img,             # image you're writing on
                str(game.armies[index]),             # CHANGE TO TROOP NUMBER FOR EACH TERRITORY             # name to draw
                (cx, cy+16),                # location (center of region) shifted to center text
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,                     # font scale
                (0, 0, 0),             # black text
                1,                       # thickness
                cv2.LINE_AA,
            )           
        index += 1
            

    open_image(canvas, labeled_img)# image you're writing on



#edge detector
def detect_edges(canvas):
    global regions, edges
    clicked = False

    # Convert to grayscale and detect edges
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.adaptiveThreshold(blurred, 255,
                              cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                              cv2.THRESH_BINARY_INV, 11, 2)
    
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)


    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    regions = [cv2.approxPolyDP(cnt, 3, True) for cnt in contours]

    update_region(canvas, edges, clicked, "")



#actual game
def gamespace():
    
    root = tk.Tk()
    root.title("Risk Game")
    root.state("zoomed")

    global canvas
    canvas = tk.Label(root)
    canvas.pack()

  

    
 


    #open image and detect edges
    global img_cv
    image_path = 'interface/riskboard_resized.jpg'
    img_cv = cv2.imread(image_path)
    
    open_image(canvas,img_cv)
    detect_edges(canvas)

    #space does space function
    canvas.bind("<Button-1>", on_click)

    class TextRedirector:
        def __init__(self, widget):
            self.widget = widget

        def write(self, text):
            self.widget.config(state='normal')         # Temporarily unlock
            self.widget.insert(tk.END, text)           # Insert text
            self.widget.see(tk.END)                    # Auto-scroll
            self.widget.config(state='disabled')       # Lock it again

        def flush(self):
            pass  # Required for Python's I/O system

    #ai output log
    output_log = ScrolledText(root, width=80, height=5, state='disabled')
    output_log.pack(padx=10, pady=10)


    sys.stdout = TextRedirector(output_log)


    global button_pressed
    button_pressed = tk.BooleanVar()
    
    global next_stage_button

    next_stage_button = tk.Button(root, text="Next Stage", command=next_stage)
    next_stage_button.pack(pady=10)
    next_stage_button.place(x=240,y=530)

    next_stage_button.config(state="disabled")

    global confirm_action_button

    confirm_action_button = tk.Button(root, text="Confirm Action", command=confirm_action)
    confirm_action_button.pack(pady=10)
    confirm_action_button.place(x=240,y=700)

    confirm_action_button.config(state="disabled")

    global instruction_text, output_text, phase_label, value_label, start_terr_text, end_terr_text

    instruction_text = tk.Label(root, text="")
    instruction_text.pack()

    global output_text_matrix
    output_text_matrix = []

    output_text = tk.Label(root, text="")
    output_text.pack()

    phase_label = tk.Label(root, text=f"Current Game Phase: {game_phase}")
    phase_label.pack()

    start_terr_text = tk.Label(root, text=f"Start Territory: {start_terr_name}")
    start_terr_text.pack()

    global end_terr_text
    end_terr_text = tk.Label(root, text=f"End Territory: {start_terr_name}")
    end_terr_text.pack()

    global available_troops_label
    available_troops_label = tk.Label(root, text=f"You have {available_deployable_troops} troops to deploy")
    available_troops_label.pack()

    global troop_var
    troop_var = tk.StringVar()
    troop_var.trace_add("write", on_troop_entry_change)  # Live update

    vcmd = (root.register(validate_int_input), "%P")
    troop_entry = tk.Entry(root, textvariable=troop_var, validate="key", validatecommand=vcmd)
    troop_entry.pack() 
    
def clear_territories():
    global start_terr_name, end_terr_name
    start_terr_name = ""
    end_terr_name = ""
    update_start_label()


def validate_int_input(value):
    return value.isdigit() or value == ""

def on_troop_entry_change(*args):
    global troop_amount_selection
    val = troop_var.get()
    troop_amount_selection = int(val) if val.isdigit() else 0
    
    print("Updated troops:", troop_amount_selection) 

def output_message(message):
    output_text_matrix.append(message)
    output_text.config(text=("".join(output_text_matrix)))
    root1.after(3000, lambda: (output_text_matrix.pop(0), output_text.config(text=("".join(output_text_matrix)))))

def update_instructions(): 
    global game_phase
    match game_phase:
        case "deploy":
            instruction_text.config(text="Deployment Phase: Click on your regions to deploy troops.")
        case "attack":
            instruction_text.config(text="Attack Phase: Click your region, then click an adjacent enemy region to attack.")
        case "fortify":
            instruction_text.config(text="Fortify Phase: Click a region to move troops from, then one to move to.")

def disable_button(button):
    button.config(state="disabled")

def enable_button(button):
    button.config(state="active")

def update_start_label():
    global start_terr_text
    start_terr_text.config(text=f"Start Territory: {start_terr_name}")

def update_end_label():
    global end_terr_text
    end_terr_text.config(text=f"End Territory: {end_terr_name}")

def update_phase_label():
    global value_label
    phase_label.config(text=f"Current Game Phase: {game_phase}")

def update_available_troops_label():
    global available_troops_label
    available_troops_label.config(text=f"You have {available_deployable_troops} troops to deploy")

def disable_available_troops_label():
    global available_troops_label
    available_troops_label.config(text="")

def set_next_stage_button(new_text):
    global next_stage_button
    next_stage_button.config(text=new_text)

def on_space(event):
    #closes window and opens a new one
    root1.destroy()
    gamespace()

# Running actual game stuff
game: GameBoard = GameBoard()

game_phase = "Deploy"

game: GameBoard = GameBoard()

start_terr_name: str = ""
end_terr_name: str = ""

troop_amount_selection: int = 0

global available_deployable_troops

available_deployable_troops: int = calculate_deploy_troop_amount()
#gives name of region when clicked

#keep track of clicks
#################################NEED TO RESET BE
first_touch = None
Even_click = True
click_idx = 0
#Start Window

root1 = tk.Tk()
root1.geometry("895x473")
root1.title("Risk Game")

#background image
image_path1 = "interface/risk_background.jpg"
original_image1 = Image.open(image_path1)
tk_image1 = ImageTk.PhotoImage(original_image1)
image_label1 = tk.Label(root1, image=tk_image1) 
image_label1.image = tk_image1
image_label1.pack(padx=5, pady=5)

#textbox
text_label = tk.Label(root1, text="Press Space to Start Game!", fg = "#f00", bg = "#000",font=("Arial", 16, "bold"))
text_label.place(relx=0.5, rely=0.8, anchor='center') #centers textbox

root1.bind("<space>", on_space)  # bind space key
root1.mainloop()


