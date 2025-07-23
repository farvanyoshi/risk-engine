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

import player
# import random_moves

game_phase = "Deploy"

game: GameBoard = GameBoard()

start_terr_name: str = ""
end_terr_name: str = ""

troop_amount_selection: int = 0

available_deployable_troops: int = 0

#gives name of region when clicked

region_to_name = {
        163: "Alaska",
        169: "Northwest Territory",
        177: "Greenland",
        140: "Alberta",
        139: "Ontario",
        143: "Quebec",
        114: "Western United States",
        112: "Eastern United States",
        86: "Central America",
        64: "Venezuela",
        54: "Peru",
        56: "Brazil",
        25: "Argentina",
        15: "South Africa",
        9: "Madagascar",
        29: "Congo",
        49: "East Africa",
        67: "North Africa",
        61: "Egypt",
        145: "Iceland",
        127: "Great Britain",
        130: "Great Britain",
        95: "Western Europe",
        94: "Southern Europe",
        122: "Nothern Europe",
        161: "Scandinavia",
        160: "Ukraine",
        78: "Middle East",
        113: "Afghanistan",
        83: "India",
        167: "Ural",
        175: "Siberia",
        172: "Yakutsk",
        144: "Irkutsk",
        168: "Kamchatka",
        120: "Japan",
        118: "Mongolia",
        107: "China",
        69: "Siam",
        28: "Indonesia",
        36: "Indonesia",
        27: "Indonesia",
        17: "Indonesia",
        20: "Indonesia",
        43: "New Guinea",
        44: "New Guinea",
        14: "Western Australia",
        21: "Eastern Australia"
    }

def validate_int_input(new_value):
    if new_value == "" or new_value.isdigit():
        return True
    return False

game: GameBoard = GameBoard()


def next_stage():
    global game_phase
    if game.is_won():
        print("Game over!")
        return

    print(f"It is now the {'player' if game.is_player else 'AI'}'s turn")

    match game_phase:
        case "Deploy":
            available_deployable_troops: int = max(int(np.count_nonzero(game.owners == game.is_player)) // 3, 3) + territory.continent_bonus(game.is_player, game.owners)
            while deployed:

                location: str = end_terr_name
                
                i: int = territory.indexer(location)
                if i == -1:
                    output_message("Invalid territory")
                    continue

                if game.owners[i]:
                    try:
                        placing: int = int(input("How many are you placing? Enter just an integer: "))
                    except ValueError:
                        message = "Please enter a positive integer."
                        print(message)
                        output_message(message)
                        continue
                    
                    # placing == -1 is an error handling value for when the input is not valid
                    while placing > deployed or placing < 0:
                        try:
                            placing = int(input(f"Invalid number of troops. Enter a number between 0 and {deployed}: "))
                        except ValueError:
                            placing = -1
                            output_message("Please enter a positive integer.")
                            continue

                    game.armies[i] += placing
                    print(f"{placing} troops added to {location.title()}.")
                    deployed -= placing
                else:
                    output_message("You don't own that territory!")
        case "Attack":
            pass
        case "Fortify":
            pass

    if game.is_player:
        # player.deploy(game)
        # player.attack(game)
        # player.fortify(game)
        game.is_player = False
    else:
        pass
        # random_moves.deploy(game)
        # update_region(canvas, edges)
        # random_moves.attack(game)
        # update_region(canvas, edges)
        # random_moves.fortify(game)
        # update_region(canvas, edges)
        game.is_player = True

    next_stage()
    root1.mainloop()

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
            except KeyError:
                pass
    #if deploy_stage:
            #exception
            if region_num != 170 and region_num != 176 and region_num != 74 and region_num != 76 and region_num !=85 and region_num != 96 and region_num != 59 and region_num != 63 and region_num != 37 and region_num != 136 and region_num != 133 and region_num != 152 and region_num != 155 and region_num != 91 and region_num != 117 and region_num != 138 and region_num != 111:
                update_region(canvas, edges, clicked, region_num)

    

    region_input(region_name)




def region_input(name_of_region):
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


# opens risk board image
def open_image(canvas, img_cv):

    
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)
    img_tk = ImageTk.PhotoImage(img_pil)

    canvas.configure(image=img_tk)
    canvas.image = img_tk


#########MAKE NEW FUNCTION CALLED UPDATE BOARD NUMB TO UPDATE TROOP NUMBER AND OWNERSHIP
def update_region(canvas, edges, clicked, region_numb):
    #light background
    labeled_img = np.ones((edges.shape[0], edges.shape[1], 3), dtype=np.uint8) * 255  # White background
    labeled_img[edges != 0] = (0, 0, 0)

    if clicked == True:
        clicked = False
        region = regions[region_numb - 1]
        if region_numb == 20 or region_numb == 28 or region_numb == 27 or region_numb ==17 or region_numb ==36:
            cv2.drawContours(labeled_img, [regions[27]], -1, (255, 0, 0), 10)
            cv2.drawContours(labeled_img, [regions[26]], -1, (255, 0, 0), 10)
            cv2.drawContours(labeled_img, [regions[16]], -1, (255, 0, 0), 10)
            cv2.drawContours(labeled_img, [regions[35]], -1, (255, 0, 0), 10)
        cv2.drawContours(labeled_img, [region], -1, (255, 0, 0), 10)
    # Functionality: labels 
    index = 0
    for region_num, region_name in region_to_name.items():
        if region_num == 27 or region_num == 17 or region_num == 20 or region_num ==36 or region_num ==43 or region_num == 130:
            continue

            # Skip if the region number is out of bounds
        if region_num - 1 < 0 or region_num - 1 >= len(regions):
            continue
        
        
        #if clicked == True:
        #    clicked = False
            #if region
        #    cv2.drawContours(labeled_img, [region], -1, (255, 0, 0), 10)

        region = regions[region_num - 1]  # get the contour by index
        ###########################NEED TO CONNECT INDONESIA

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


    end_terr_text = tk.Label(root, text=f"End Territory: {start_terr_name}")
    end_terr_text.pack()


    global max_troops
    max_troops = 10
    max_entry = tk.Label(root, text=f"You have {max_troops} troops to deploy")
    max_entry.pack()

    global troop_var
    troop_var = tk.StringVar()
    troop_var.trace_add("write", on_troop_entry_change)  # Live update

    vcmd = (root.register(validate_int_input), "%P")
    troop_entry = tk.Entry(root, textvariable=troop_var, validate="key", validatecommand=vcmd)
    troop_entry.pack() 
    

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


def update_start_label():
    start_terr_text.config(text=f"Start Territory: {start_terr_name}")

def update_end_label():
    end_terr_text.config(text=f"End Territory: {end_terr_name}")

def update_phase_label():
    value_label.config(text=game_phase)

def on_space(event):
    #closes window and opens a new one
    root1.destroy()
    gamespace()


def wait_for_input():
    next_stage_button.config(state="normal")
    button_pressed.set(False)
    root1.wait_variable(button_pressed)
    print("Button pressed! Continuing logic...")
    next_stage_button.config(state="disabled")

def next_stage():
    button_pressed.set(True)


game: GameBoard = GameBoard()

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


