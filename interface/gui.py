import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk
import cv2
import numpy as np
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from gameboard import GameBoard
import engine
import random_moves
import territory

INTERFACE_DIR = os.path.dirname(os.path.abspath(__file__))

# Region numbers that are extra pieces of a territory that already has a main region (Indonesia, New Guinea, Great Britain)
EXTRA_REGIONS = (17, 20, 27, 36, 43, 130)
# The pieces of Indonesia, drawn together so the whole territory is one color
INDONESIA_REGIONS = (28, 27, 36, 17)

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

def validate_int_input(value):
    return value.isdigit() or value == ""

def loop_game_stage():
    global game_phase, available_deployable_troops
    if game.is_won():
        return
    if game_phase == "Deploy":
        set_next_stage_button("Skip Stage")
        disable_available_troops_label()
        game_phase = "Attack"
    elif game_phase == "Attack":
        set_next_stage_button("Skip Stage")
        game_phase = "Fortify"
    elif game_phase == "Fortify":
        ai_play()
        if game.is_won():
            return
        set_next_stage_button("Next Stage")
        game_phase = "Deploy"
        disable_button(next_stage_button)
        available_deployable_troops = game.deploy_count(True)
        update_available_troops_label()

    enable_button(confirm_action_button)
    clear_territories()

    update_phase_label()
    update_instructions()
    output_message(game_phase)

def ai_play():
    ai = random_moves if easy_ai else engine
    print("It is now the AI's turn")
    ai.deploy(game, False)
    ai.attack(game, False)
    if not game.is_won():
        ai.fortify(game, False)
    update_region()
    check_game_over()
    print("It is now the player's turn")

def check_game_over() -> bool:
    winner = game.winner()
    if winner is None:
        return False
    message = "The player has won the game!" if winner else "The AI has won the game!"
    print(message)
    instruction_text.config(text=message)
    disable_button(next_stage_button)
    disable_button(confirm_action_button)
    return True

def next_stage():
    loop_game_stage()

def confirm_action():
    input_action()

def input_action():
    global available_deployable_troops

    if game.is_won():
        return

    match game_phase:
        case "Deploy":
            i: int = territory.indexer(start_terr_name.lower())

            if i != -1 and game.owners[i] and 0 < troop_amount_selection <= available_deployable_troops:
                game.armies[i] += troop_amount_selection
                print(f"{troop_amount_selection} troops added to {start_terr_name.title()}.")
                available_deployable_troops -= troop_amount_selection
                update_available_troops_label()
                if available_deployable_troops == 0:
                    enable_button(next_stage_button)
                    disable_button(confirm_action_button)
                clear_territories()
            else:
                output_message("Invalid: click one of your territories and enter a number of troops you have left")

        case "Attack":
            start_index: int = territory.indexer(start_terr_name.lower())
            end_index: int = territory.indexer(end_terr_name.lower())

            if start_index != -1 and end_index != -1 and game.can_attack(True, start_index, end_index, troop_amount_selection):
                game.battle(start_index, end_index, troop_amount_selection)
                print(f"Attacked {end_terr_name.title()} from {start_terr_name.title()} with {troop_amount_selection} troops")
                if game.owners[end_index]:
                    output_message(f"Captured {end_terr_name.title()}!")
                set_next_stage_button("Next Stage")
                clear_territories()
                if check_game_over():
                    update_region()
                    return
            else:
                output_message("Invalid: click your territory, then a bordering enemy, and send between 1 and one less than your troops")

        case "Fortify":
            start_index = territory.indexer(start_terr_name.lower())
            end_index = territory.indexer(end_terr_name.lower())

            if start_index != -1 and end_index != -1 and game.can_fortify(True, start_index, end_index, troop_amount_selection):
                game.fortify(start_index, end_index, troop_amount_selection)
                print(f"Fortified {end_terr_name.title()} from {start_terr_name.title()} with {troop_amount_selection} troops")
                set_next_stage_button("Next Stage")
                disable_button(confirm_action_button)
                clear_territories()
            else:
                output_message("Invalid: pick two of your connected territories and leave at least 1 troop behind")

    update_region()

def on_click(event):
    for i, region in enumerate(regions):
        region_num = i+1
        if cv2.pointPolygonTest(region, (event.x, event.y), False) >= 0:
            try:
                region_name = region_to_name[region_num]
            except KeyError:
                continue
            match game_phase:
                case "Deploy":
                    deploy_region_input(region_name)
                case "Attack" | "Fortify":
                    two_region_input(region_name)
            break

def deploy_region_input(name_of_region):
    global start_terr_name
    if start_terr_name == name_of_region:
        start_terr_name = ""
    else:
        start_terr_name = name_of_region

    update_start_label()

# Attack and fortify both pick a starting territory and then an ending territory
def two_region_input(name_of_region):
    global start_terr_name, end_terr_name
    if start_terr_name == "":
        start_terr_name = name_of_region
    elif start_terr_name == name_of_region and end_terr_name == "":
        start_terr_name = ""
    elif end_terr_name == "":
        end_terr_name = name_of_region
    elif end_terr_name == name_of_region:
        end_terr_name = ""
    else:
        output_message("Click a selected territory again to unselect it")

    update_start_label()
    update_end_label()

# opens risk board image
def open_image(canvas, img_cv):
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)
    img_tk = ImageTk.PhotoImage(img_pil)

    canvas.configure(image=img_tk)
    canvas.image = img_tk

# Redraws the map: green for the player, red for the AI, with names and troop counts
def update_region():
    #light background
    labeled_img = np.ones((edges.shape[0], edges.shape[1], 3), dtype=np.uint8) * 255  # White background
    labeled_img[edges != 0] = (0, 0, 0)

    for region_num, region_name in region_to_name.items():
        # Skip extra pieces and region numbers that are out of bounds
        if region_num in EXTRA_REGIONS or region_num - 1 >= len(regions):
            continue

        index: int = territory.indexer(region_name.lower())
        region = regions[region_num - 1]  # get the contour by index

        #colors for each region based on owner
        color = (0, 255, 0) if game.owners[index] else (0, 0, 255)
        pieces = INDONESIA_REGIONS if region_num == 28 else (region_num,)
        for piece in pieces:
            cv2.drawContours(labeled_img, [regions[piece - 1]], -1, color, thickness=cv2.FILLED)

        # Calculate center of the region using image moments
        M = cv2.moments(region)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])

            # Draw the name and troop count on the image
            cv2.putText(labeled_img, region_name, (cx-22, cy+5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(labeled_img, str(game.armies[index]), (cx, cy+16), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1, cv2.LINE_AA)

    open_image(canvas, labeled_img)

#edge detector
def detect_edges():
    global regions, edges

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

    update_region()

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

#actual game
def gamespace():
    global root, canvas, img_cv
    root = tk.Tk()
    root.title("Risk Game")
    try:
        root.state("zoomed")  # Windows
    except tk.TclError:
        root.attributes("-zoomed", True)  # Linux

    canvas = tk.Label(root)
    canvas.pack()

    #open image and detect edges
    img_cv = cv2.imread(os.path.join(INTERFACE_DIR, 'riskboard_resized.jpg'))

    open_image(canvas, img_cv)
    detect_edges()

    canvas.bind("<Button-1>", on_click)

    #ai output log
    output_log = ScrolledText(root, width=80, height=5, state='disabled')
    output_log.pack(padx=10, pady=10)

    sys.stdout = TextRedirector(output_log)

    global next_stage_button, confirm_action_button

    next_stage_button = tk.Button(root, text="Next Stage", command=next_stage)
    next_stage_button.place(x=240,y=530)
    disable_button(next_stage_button)

    confirm_action_button = tk.Button(root, text="Confirm Action", command=confirm_action)
    confirm_action_button.place(x=240,y=700)

    global instruction_text, output_text, phase_label, start_terr_text, end_terr_text, available_troops_label, output_text_matrix

    instruction_text = tk.Label(root, text="")
    instruction_text.pack()

    output_text_matrix = []

    output_text = tk.Label(root, text="")
    output_text.pack()

    phase_label = tk.Label(root, text=f"Current Game Phase: {game_phase}")
    phase_label.pack()

    start_terr_text = tk.Label(root, text=f"Start Territory: {start_terr_name}")
    start_terr_text.pack()

    end_terr_text = tk.Label(root, text=f"End Territory: {end_terr_name}")
    end_terr_text.pack()

    available_troops_label = tk.Label(root, text=f"You have {available_deployable_troops} troops to deploy")
    available_troops_label.pack()

    global troop_var
    troop_var = tk.StringVar()
    troop_var.trace_add("write", on_troop_entry_change)  # Live update

    vcmd = (root.register(validate_int_input), "%P")
    troop_entry = tk.Entry(root, textvariable=troop_var, validate="key", validatecommand=vcmd)
    troop_entry.pack()

    update_instructions()
    print("It is now the player's turn")

def clear_territories():
    global start_terr_name, end_terr_name
    start_terr_name = ""
    end_terr_name = ""
    update_start_label()
    update_end_label()

def on_troop_entry_change(*args):
    global troop_amount_selection
    val = troop_var.get()
    troop_amount_selection = int(val) if val.isdigit() else 0

def output_message(message):
    output_text_matrix.append(message + "\n")
    output_text.config(text=("".join(output_text_matrix)))
    root.after(3000, lambda: (output_text_matrix.pop(0), output_text.config(text=("".join(output_text_matrix)))))

def update_instructions():
    match game_phase:
        case "Deploy":
            instruction_text.config(text="Deployment Phase: Click one of your regions, type a troop amount, and press Confirm Action.")
        case "Attack":
            instruction_text.config(text="Attack Phase: Click your region, then an adjacent enemy region, type a troop amount, and press Confirm Action.")
        case "Fortify":
            instruction_text.config(text="Fortify Phase: Click a region to move troops from, then one to move to, type a troop amount, and press Confirm Action.")

def disable_button(button):
    button.config(state="disabled")

def enable_button(button):
    button.config(state="normal")

def update_start_label():
    start_terr_text.config(text=f"Start Territory: {start_terr_name}")

def update_end_label():
    end_terr_text.config(text=f"End Territory: {end_terr_name}")

def update_phase_label():
    phase_label.config(text=f"Current Game Phase: {game_phase}")

def update_available_troops_label():
    available_troops_label.config(text=f"You have {available_deployable_troops} troops to deploy")

def disable_available_troops_label():
    available_troops_label.config(text="")

def set_next_stage_button(new_text):
    next_stage_button.config(text=new_text)

def on_space(event):
    #closes window and opens a new one
    start_window.destroy()
    gamespace()

def run(easy: bool = False):
    global game, game_phase, start_terr_name, end_terr_name, troop_amount_selection, available_deployable_troops, easy_ai, start_window

    game = GameBoard()
    game_phase = "Deploy"
    easy_ai = easy

    start_terr_name = ""
    end_terr_name = ""
    troop_amount_selection = 0
    available_deployable_troops = game.deploy_count(True)

    #Start Window
    start_window = tk.Tk()
    start_window.geometry("895x473")
    start_window.title("Risk Game")

    #background image
    original_image1 = Image.open(os.path.join(INTERFACE_DIR, "risk_background.jpg"))
    tk_image1 = ImageTk.PhotoImage(original_image1)
    image_label1 = tk.Label(start_window, image=tk_image1)
    image_label1.image = tk_image1
    image_label1.pack(padx=5, pady=5)

    #textbox
    text_label = tk.Label(start_window, text="Press Space to Start Game!", fg = "#f00", bg = "#000",font=("Arial", 16, "bold"))
    text_label.place(relx=0.5, rely=0.8, anchor='center') #centers textbox

    start_window.bind("<space>", on_space)  # bind space key
    start_window.mainloop()

if __name__ == "__main__":
    run()
