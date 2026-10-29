import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk
import cv2
import numpy as np
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import cards
import gameboard
from gameboard import GameBoard
import engine
import random_moves
import territory

INTERFACE_DIR = os.path.dirname(os.path.abspath(__file__))

# Region numbers that are extra pieces of a territory that already has a main region (Indonesia, New Guinea, Great Britain)
EXTRA_REGIONS = (17, 20, 27, 36, 43, 130)
# The pieces of Indonesia, drawn together so the whole territory is one color
INDONESIA_REGIONS = (28, 27, 36, 17)

# Map colors for each player, in the same order as gameboard.PLAYER_COLORS (OpenCV uses blue, green, red)
PLAYER_BGR = [(0, 255, 0), (0, 0, 255), (255, 170, 60), (0, 230, 255), (220, 120, 200), (0, 150, 255)]

# Milliseconds between AI turns, so the map can be seen changing
AI_TURN_DELAY = 700

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
    global game_phase
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
        end_turn()
        return

    enable_button(confirm_action_button)
    clear_territories()

    update_phase_label()
    update_instructions()
    refresh_deploy_controls()
    output_message(game_phase)

def is_human(player: int) -> bool:
    return player < num_humans

# Passes the turn to the next player still in the game
def end_turn():
    global current_player, turns

    # capturing a territory this turn earns the top card of the deck
    card = game.end_turn(current_player)
    if card is not None:
        print(f"{gameboard.player_name(current_player, num_humans)} earned a card: {cards.card_name(card)}")

    current_player = game.next_player(current_player)
    turns += 1
    update_player_label()
    print(f"It is now {gameboard.player_name(current_player, num_humans)}'s turn")

    if is_human(current_player):
        start_human_turn()
    else:
        # AI turns run one at a time on a timer so the window keeps updating
        disable_button(next_stage_button)
        disable_button(confirm_action_button)
        refresh_deploy_controls()
        instruction_text.config(text=f"{gameboard.player_name(current_player, num_humans)} is playing...")
        root.after(AI_TURN_DELAY, ai_play)

def start_human_turn():
    global game_phase, available_deployable_troops
    game.start_turn(current_player)
    game_phase = "Deploy"
    available_deployable_troops = game.deploy_count(current_player)
    set_next_stage_button("Next Stage")
    clear_territories()
    update_available_troops_label()
    update_phase_label()
    update_instructions()
    refresh_deploy_controls()

def is_deploy_phase() -> bool:
    return game_phase in ("Deploy", "Card Deploy")

# Turns the deploy and trade buttons on or off: the player can't move on while troops are left or a trade is forced
def refresh_deploy_controls():
    update_cards_label()
    if not is_deploy_phase() or not is_human(current_player) or game.is_won():
        disable_button(trade_best_button)
        disable_button(trade_button)
        return

    forced: bool = game.must_trade(current_player)
    has_set: bool = bool(cards.all_sets(game.hands[current_player]))
    for button in (trade_best_button, trade_button):
        (enable_button if has_set else disable_button)(button)
    (enable_button if available_deployable_troops > 0 else disable_button)(confirm_action_button)

    if forced:
        disable_button(next_stage_button)
        instruction_text.config(text=f"You have {len(game.hands[current_player])} cards, so you must trade a set (Trade Best Set, or type card numbers and press Trade).")
        return
    update_instructions()

    if available_deployable_troops == 0:
        if game_phase == "Card Deploy":
            back_to_attack()
        else:
            enable_button(next_stage_button)
    else:
        disable_button(next_stage_button)

# Hands are open information (the deck order is public anyway), so this shows the current player's cards
def update_cards_label():
    hand = game.hands[current_player]
    held = "  ".join(f"{number}. {cards.card_name(card)}" for number, card in enumerate(hand, 1)) or "none"
    others = ", ".join(f"{gameboard.PLAYER_COLORS[p]} {len(game.hands[p])}" for p in game.alive_players() if p != current_player)
    cards_text.config(text=f"{gameboard.PLAYER_COLORS[current_player]}'s cards: {held}   |   Next set: {cards.set_value(game.sets_traded)} troops   |   Others hold: {others}")

def trade_best():
    trade_set(cards.best_set(game.hands[current_player], game.owned(current_player)))

def trade_selected():
    hand = game.hands[current_player]
    try:
        traded = [hand[int(number) - 1] for number in trade_var.get().replace(',', ' ').split()]
    except (ValueError, IndexError):
        traded = None
    trade_set(traded)

def trade_set(traded):
    global available_deployable_troops
    if not is_deploy_phase() or traded is None or not cards.is_valid_set(traded):
        output_message("Not a set: pick three of the same symbol, one of each symbol, or any two cards with a wild")
        return
    gained, bonus = game.trade(current_player, traded)
    available_deployable_troops += gained
    message = cards.trade_message(gameboard.PLAYER_COLORS[current_player], traded, gained, bonus)
    print(message)
    output_message(message)
    trade_var.set("")
    update_available_troops_label()
    update_region()
    refresh_deploy_controls()

# Taking an eliminated player's cards and ending up with 6 or more means trading and placing those troops before attacking again
def enter_card_deploy():
    global game_phase, available_deployable_troops
    game_phase = "Card Deploy"
    available_deployable_troops = 0
    disable_button(next_stage_button)
    clear_territories()
    update_available_troops_label()
    update_phase_label()
    refresh_deploy_controls()

def back_to_attack():
    global game_phase
    game_phase = "Attack"
    disable_available_troops_label()
    enable_button(confirm_action_button)
    enable_button(next_stage_button)
    set_next_stage_button("Next Stage")
    update_phase_label()
    update_instructions()
    update_cards_label()

def ai_play():
    if num_humans == 0 and turns >= gameboard.AI_ONLY_TURN_LIMIT:
        message = f"No winner after {turns} turns. Most territories: {gameboard.player_name(game.standings()[0][0], num_humans)}"
        print(message)
        instruction_text.config(text=message)
        return

    ai = random_moves if easy_ai else engine
    alive_before = game.alive_players()
    game.start_turn(current_player)
    ai.deploy(game, current_player)
    ai.attack(game, current_player)
    if not game.is_won():
        ai.fortify(game, current_player)
    announce_eliminations(alive_before)
    update_region()
    if not check_game_over():
        end_turn()

def announce_eliminations(alive_before):
    for p in alive_before:
        if not game.is_alive(p):
            message = f"{gameboard.player_name(p, num_humans)} has been eliminated, and {gameboard.PLAYER_COLORS[current_player]} takes their cards!"
            print(message)
            output_message(message)

def check_game_over() -> bool:
    winner = game.winner()
    if winner is None:
        return False
    message = f"{gameboard.player_name(winner, num_humans)} has won the game!"
    print(message)
    instruction_text.config(text=message)
    disable_button(next_stage_button)
    disable_button(confirm_action_button)
    disable_button(trade_best_button)
    disable_button(trade_button)
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
        case "Deploy" | "Card Deploy":
            i: int = territory.indexer(start_terr_name.lower())

            if i != -1 and game.owners[i] == current_player and 0 < troop_amount_selection <= available_deployable_troops:
                game.armies[i] += troop_amount_selection
                print(f"{gameboard.PLAYER_COLORS[current_player]} added {troop_amount_selection} troops to {start_terr_name.title()}.")
                available_deployable_troops -= troop_amount_selection
                update_available_troops_label()
                clear_territories()
                refresh_deploy_controls()
            else:
                output_message("Invalid: click one of your territories and enter a number of troops you have left")

        case "Attack":
            start_index: int = territory.indexer(start_terr_name.lower())
            end_index: int = territory.indexer(end_terr_name.lower())

            if start_index != -1 and end_index != -1 and game.can_attack(current_player, start_index, end_index, troop_amount_selection):
                alive_before = game.alive_players()
                game.battle(start_index, end_index, troop_amount_selection)
                print(f"{gameboard.PLAYER_COLORS[current_player]} attacked {end_terr_name.title()} from {start_terr_name.title()} with {troop_amount_selection} troops")
                if game.owners[end_index] == current_player:
                    output_message(f"Captured {end_terr_name.title()}!")
                announce_eliminations(alive_before)
                set_next_stage_button("Next Stage")
                clear_territories()
                if check_game_over():
                    update_region()
                    return
                if game.must_trade(current_player, cards.ELIMINATION_TRADE_HAND):
                    output_message("You took their cards: trade down to 4 or fewer, then place the troops")
                    enter_card_deploy()
                update_cards_label()
            else:
                output_message("Invalid: click your territory, then a bordering enemy, and send between 1 and one less than your troops")

        case "Fortify":
            start_index = territory.indexer(start_terr_name.lower())
            end_index = territory.indexer(end_terr_name.lower())

            if start_index != -1 and end_index != -1 and game.can_fortify(current_player, start_index, end_index, troop_amount_selection):
                game.fortify(start_index, end_index, troop_amount_selection)
                print(f"{gameboard.PLAYER_COLORS[current_player]} fortified {end_terr_name.title()} from {start_terr_name.title()} with {troop_amount_selection} troops")
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
                case "Deploy" | "Card Deploy":
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

# Redraws the map in each owner's color, with names and troop counts
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
        color = PLAYER_BGR[game.owners[index]]
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

    global instruction_text, output_text, phase_label, start_terr_text, end_terr_text, available_troops_label, output_text_matrix

    instruction_text = tk.Label(root, text="")
    instruction_text.pack()

    output_text_matrix = []

    output_text = tk.Label(root, text="")
    output_text.pack()

    phase_label = tk.Label(root, text=f"Current Game Phase: {game_phase}", font=("Arial", 11, "bold"))
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

    global cards_text
    cards_text = tk.Label(root, text="")
    cards_text.pack()

    # buttons sit in a row under the troop entry so they never cover the labels
    global next_stage_button, confirm_action_button, trade_best_button, trade_button, trade_var
    buttons = tk.Frame(root)
    buttons.pack(pady=5)

    confirm_action_button = tk.Button(buttons, text="Confirm Action", command=confirm_action)
    confirm_action_button.pack(side=tk.LEFT, padx=10)

    next_stage_button = tk.Button(buttons, text="Next Stage", command=next_stage)
    next_stage_button.pack(side=tk.LEFT, padx=10)
    disable_button(next_stage_button)

    # trading cards: the best set, or the card numbers typed in the box (like "1 3 4")
    trade_best_button = tk.Button(buttons, text="Trade Best Set", command=trade_best)
    trade_best_button.pack(side=tk.LEFT, padx=(30, 5))
    trade_var = tk.StringVar()
    tk.Entry(buttons, textvariable=trade_var, width=8).pack(side=tk.LEFT)
    trade_button = tk.Button(buttons, text="Trade", command=trade_selected)
    trade_button.pack(side=tk.LEFT, padx=5)
    disable_button(trade_best_button)
    disable_button(trade_button)

    print("Players: " + ", ".join(gameboard.player_name(p, num_humans) for p in range(game.num_players)))
    update_player_label()
    print(f"It is now {gameboard.player_name(current_player, num_humans)}'s turn")
    if is_human(current_player):
        start_human_turn()
    else:
        disable_button(confirm_action_button)
        refresh_deploy_controls()
        instruction_text.config(text=f"{gameboard.player_name(current_player, num_humans)} is playing...")
        root.after(AI_TURN_DELAY, ai_play)

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
            instruction_text.config(text="Deployment Phase: Click one of your regions, type a troop amount, and press Confirm Action. Trade cards for more troops.")
        case "Card Deploy":
            instruction_text.config(text="Card Deploy: place the troops from your traded cards, then you can keep attacking.")
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

# The phase label also shows whose turn it is, in their color
def update_player_label():
    update_phase_label()

def update_phase_label():
    b, g, r = PLAYER_BGR[current_player]
    phase_label.config(text=f"Current Player: {gameboard.player_name(current_player, num_humans)}  |  Current Game Phase: {game_phase}", bg=f"#{r:02x}{g:02x}{b:02x}")

def update_available_troops_label():
    available_troops_label.config(text=f"{gameboard.PLAYER_COLORS[current_player]} has {available_deployable_troops} troops to deploy")

def disable_available_troops_label():
    available_troops_label.config(text="")

def set_next_stage_button(new_text):
    next_stage_button.config(text=new_text)

def on_space(event):
    start_game()

# Reads the player choices, then closes the start window and opens the game
def start_game():
    global game, game_phase, num_humans, current_player, turns, easy_ai, start_terr_name, end_terr_name, troop_amount_selection, available_deployable_troops
    try:
        humans, ais = int(humans_var.get()), int(ais_var.get())
    except ValueError:
        start_error.config(text="Enter whole numbers of players")
        return
    problem = gameboard.check_player_counts(humans, ais)
    if problem:
        start_error.config(text=problem)
        return

    num_humans = humans
    easy_ai = bool(easy_var.get())
    game = GameBoard(humans + ais)
    game_phase = "Deploy"
    current_player = 0
    turns = 0

    start_terr_name = ""
    end_terr_name = ""
    troop_amount_selection = 0
    available_deployable_troops = game.deploy_count(current_player)

    #closes window and opens a new one
    start_window.destroy()
    gamespace()

def run(easy: bool = False, humans: int | None = None, ais: int | None = None):
    global start_window, humans_var, ais_var, easy_var, start_error

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

    #player choice: how many humans and AIs
    choices = tk.Frame(start_window, bg = "#000")
    choices.place(relx=0.5, rely=0.62, anchor='center')

    humans_var = tk.StringVar(value = str(1 if humans is None else humans))
    ais_var = tk.StringVar(value = str(1 if ais is None else ais))
    easy_var = tk.IntVar(value = int(easy))

    tk.Label(choices, text="Humans", fg = "#fff", bg = "#000", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=5, pady=5)
    tk.Spinbox(choices, from_=0, to=gameboard.MAX_PLAYERS, width=3, textvariable=humans_var, font=("Arial", 12)).grid(row=0, column=1, padx=5)
    tk.Label(choices, text="AIs", fg = "#fff", bg = "#000", font=("Arial", 12, "bold")).grid(row=0, column=2, padx=5)
    tk.Spinbox(choices, from_=0, to=gameboard.MAX_PLAYERS, width=3, textvariable=ais_var, font=("Arial", 12)).grid(row=0, column=3, padx=5)
    tk.Checkbutton(choices, text="Easy AI", variable=easy_var, fg = "#fff", bg = "#000", selectcolor = "#333", activebackground = "#000", activeforeground = "#fff").grid(row=0, column=4, padx=5)
    tk.Button(choices, text="Start", command=start_game).grid(row=0, column=5, padx=5)

    start_error = tk.Label(choices, text="", fg = "#f00", bg = "#000")
    start_error.grid(row=1, column=0, columnspan=6)

    #textbox
    text_label = tk.Label(start_window, text=f"Choose {gameboard.MIN_PLAYERS} to {gameboard.MAX_PLAYERS} players, then press Space or Start!", fg = "#f00", bg = "#000",font=("Arial", 16, "bold"))
    text_label.place(relx=0.5, rely=0.8, anchor='center') #centers textbox

    start_window.bind("<space>", on_space)  # bind space key
    start_window.mainloop()

if __name__ == "__main__":
    run()
