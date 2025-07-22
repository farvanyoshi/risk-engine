import tkinter as tk
from PIL import Image, ImageTk
import cv2
import numpy as np
#allows gameboard to be imported
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from gameboard import GameBoard
GameBoard=GameBoard()
#gives troop_num the values of gamebaord.armies
global troop_num
global owners
owners = GameBoard.owners
troop_num = GameBoard.armies


#gives name of region when clicked

region_to_name = {
        113: "Afghanistan",
        163: "Alaska",
        140: "Alberta",
        25: "Argentina",
        56: "Brazil",
        86: "C. America",
        107: "China",
        29: "Congo",
        49: "E. Africa",
        21: "E. Australia",
        112: "E. United States",
        61: "Egypt",
        127: "G. Britain",
        177: "Greenland",
        145: "Iceland",
        83: "India",
        28: "Indonesia",
        144: "Irkutsk",
        120: "Japan",
        168: "Kamchatka",
        9: "Madagascar",
        78: "M. East",
        118: "Mongolia",
        44: "New Guinea",
        67: "N. Africa",
        122: "N. Europe",
        169: "N. Territory",
        139: "Ontario",
        54: "Peru",
        143: "Quebec",
        160: "Russia",
        161: "Scandinavia",
        69: "Siam",
        175: "Siberia",
        15: "S. Africa",
        94: "S. Europe",
        167: "Ural",
        64: "Venezuela",
        14: "W. Australia",
        95: "W. Europe",
        114: "W. United States",
        172: "Yakutsk",
        36: "Indonesia",
        27: "Indonesia",
        17: "Indonesia",
        20: "Indonesia",
        43: "New Guinea",
        130: "Great Britain"
    }

def next_stage():
    ######################NEED TO GO TO NEXT STAGE
    '''
    if turn == player:
        if stage == deploy_phase:
            stage = attack_phase:
        if stage == attack_phase:
            stage = fortify_phase:
        if stage == fortify_phase:
            turn = ai
            stage = deploy_phase
    if turn == ai:
        if stage == deploy_phase:
            stage = attack_phase
        if stage == attack_phase:
            stage = fortify_phase
        if stage == fortify_phase:
            turn = player
            stage = deploy_phase
'''



def on_click(event):
    region_name = "Not a Region"
    #print(f"Mouse clicked at {event.x}, {event.y}")
    for i, region in enumerate(regions):
        region_num = i+1
        if cv2.pointPolygonTest(region, (event.x, event.y), False) >= 0:
            print(f"Clicked inside region {region_num}")
            try:
                region_name = region_to_name[region_num]
            except KeyError:
                pass

  
    print(region_name)


# opens risk board image
def open_image(canvas, img_cv):

    
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)
    img_tk = ImageTk.PhotoImage(img_pil)

    canvas.configure(image=img_tk)
    canvas.image = img_tk


#########MAKE NEW FUNCTION CALLED UPDATE BOARD NUMB TO UPDATE TROOP NUMBER AND OWNERSHIP
def update_region(canvas, edges):
    #light background
    labeled_img = np.ones((edges.shape[0], edges.shape[1], 3), dtype=np.uint8) * 255  # White background
    labeled_img[edges != 0] = (0, 0, 0)

    
    # Functionality: labels 
    index = 0
    for region_num, region_name in region_to_name.items():
        if region_num == 27 or region_num == 17 or region_num == 20 or region_num ==36 or region_num ==43 or region_num == 130:
            continue

            # Skip if the region number is out of bounds
        if region_num - 1 < 0 or region_num - 1 >= len(regions):
            continue
        

        region = regions[region_num - 1]  # get the contour by index
        ###########################NEED TO CONNECT INDONESIA
        #colors for each region based on owner
        if owners[index] == True:
            if region_num == 28:
                #make whole indonesia one color
                cv2.drawContours(labeled_img, [regions[region_num - 1]], -1, (0,255,0), thickness=cv2.FILLED)
                cv2.drawContours(labeled_img, [regions[region_num - 2]], -1, (0,255,0), thickness=cv2.FILLED)
                cv2.drawContours(labeled_img, [regions[region_num + 7]], -1, (0,255,0), thickness=cv2.FILLED)
                cv2.drawContours(labeled_img, [regions[region_num - 12]], -1, (0,255,0), thickness=cv2.FILLED)

            cv2.drawContours(labeled_img, [region], -1, (0,255,0), thickness=cv2.FILLED)
        if owners[index]== False:
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
                (0, 0, 0),             # green text
                1,                       # thickness
                cv2.LINE_AA              # anti-aliased
            )
            cv2.putText(
                labeled_img,             # image you're writing on
                str(troop_num[index]),             # CHANGE TO TROOP NUMBER FOR EACH TERRITORY             # name to draw
                (cx, cy+16),                # location (center of region) shifted to center text
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,                     # font scale
                (0, 0, 0),             # green text
                1,                       # thickness
                cv2.LINE_AA
            )           # image you're writing on
        index += 1
            

    open_image(canvas, labeled_img)


    







#edge detector
def detect_edges(canvas):
    global regions

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
    update_region(canvas, edges)



#actual game
def gamespace():
    root = tk.Tk()
    root.title("Risk Game")
    root.state("zoomed")

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


    next_stage_button = tk.Button(root, text="Next Stage", command=next_stage)
    next_stage_button.pack(pady=10)
    next_stage_button.place(x=240,y=530)
    root.mainloop()

def on_space(event):
    #closes window and opens a new one
    root1.destroy()
    gamespace()



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