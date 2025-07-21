import tkinter as tk
from PIL import Image, ImageTk
import cv2
import numpy as np
#from gameboard import GameBoard


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

            # if region_num == 163:
            #     region_name = "Alaska"
            # elif region_num == 169:
            #     region_name = "Northwest Territory"
            # elif region_num == 177:
            #     region_name = "Greenland"
            # elif region_num == 140:
            #     region_name = "Alberta"
            # elif region_num == 139:
            #     region_name = "Ontario"
            # elif region_num == 143:
            #     region_name = "Quebec"
            # elif region_num == 114:
            #     region_name = "Western United States"
            # elif region_num == 112:
            #     region_name = "Eastern United States"
            # elif region_num == 86:
            #     region_name = "Central America"
            # elif region_num == 64:
            #     region_name = "Venezuela"
            # elif region_num == 54:
            #     region_name = "Peru"
            # elif region_num == 56:
            #     region_name = "Brazil"
            # elif region_num == 25:
            #     region_name = "Argentina"
            # elif region_num == 15:
            #     region_name = "South Africa"
            # elif region_num == 9:
            #     region_name = "Madagascar"
            # elif region_num == 29:
            #     region_name = "Congo"
            # elif region_num == 49:
            #     region_name = "East Africa"
            # elif region_num == 67:
            #     region_name = "North Africa"
            # elif region_num == 61:
            #     region_name = "Egypt"
            # elif region_num == 145:
            #     region_name = "Iceland"
            # elif region_num == 127 or region_num == 130:
            #     region_name = "Great Britain"
            # elif region_num == 95:
            #     region_name = "Western Europe"
            # elif region_num == 94:
            #     region_name = "Southern Europe"
            # elif region_num == 122:
            #     region_name = "Nothern Europe"
            # elif region_num == 161:
            #     region_name = "Scandinavia"
            # elif region_num == 160:
            #     region_name = "Ukraine"
            # elif region_num == 78:
            #     region_name = "Middle East"
            # elif region_num == 113:
            #     region_name = "Afghanistan"
            # elif region_num == 83:
            #     region_name = "India"
            # elif region_num == 167:
            #     region_name = "Ural"
            # elif region_num == 175:
            #     region_name = "Siberia"
            # elif region_num == 172:
            #     region_name = "Yakutsk"
            # elif region_num == 144:
            #     region_name = "Irkutsk"
            # elif region_num == 168:
            #     region_name = "Kamchatka"
            # elif region_num == 120:
            #     region_name = "Japan"
            # elif region_num == 118:
            #     region_name = "Mongolia"
            # elif region_num == 107:
            #     region_name = "China"
            # elif region_num == 69:
            #     region_name = "Siam"
            # elif region_num == 28 or region_num == 36 or region_num == 27 or region_num == 17 or region_num == 20:
            #     region_name = "Indonesia"
            # elif region_num == 43 or region_num == 44:
            #     region_name = "New Guinea"
            # elif region_num ==  14:
            #     region_name = "Western Australia"
            # elif region_num == 21:
            #     region_name = "Eastern Australia"
            # elif region_num == 176:
            #     pass #prevent not a region error
            # elif region_num == 178:
            #     pass
            # elif region_num == 170:
            #     pass
            # else:
            #     print("Not a Region")
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
    
    # functionality: Labels each region with their respective number
    # for idx, contour in enumerate(regions):
    #     # Get center point of contour (via moments)
    #     M = cv2.moments(contour)
    #     if M["m00"] != 0:
    #         cx = int(M["m10"] / M["m00"])
    #         cy = int(M["m01"] / M["m00"])
    #         cv2.putText(labeled_img, str(idx + 1), (cx, cy),
    #         cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    # Functionality: labels 
    for region_num, region_name in region_to_name.items():
        if region_num == 27 or region_num == 17 or region_num == 20 or region_num ==36:
            continue

            # Skip if the region number is out of bounds
        if region_num - 1 < 0 or region_num - 1 >= len(regions):
            continue
        

        region = regions[region_num - 1]  # get the contour by index

        #colors for each region based on owner

        ##########################################need to implement
        #if region_name in player:
        #    cv2.drawContours(labeled_img, [region], -1, (0,255,0), thickness=cv2.FILLED)
        #if region_name in ai:
        #    cv2.drawContours(labeled_img, [region], -1, (0,0,255), thickness=cv2.FILLED)
        
        ##need to fix MAKES region blue
        '''
        index = 0
        for i in regions:
            index += 1
            for region_num in region_to_name.items():
                if index != region_num:
                    cv2.drawContours(labeled_img, [i], -1, (255, 0, 0), thickness=cv2.FILLED)
        if region_num == 163:
            cv2.drawContours(labeled_img, [region], -1, (0, 0, 255), thickness=cv2.FILLED)  # Blue for Alaska
            '''
        # Calculate center of the region using image moments
        M = cv2.moments(region)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])

            # Draw the name on the image
            cv2.putText(
                labeled_img,             # image you're writing on
                region_name,             # name to draw
                (cx-10, cy),                # location (center of region) shifted to center text
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,                     # font scale
                (0, 255, 0),             # green text
                1,                       # thickness
                cv2.LINE_AA              # anti-aliased
            )
            cv2.putText(
                labeled_img,             # image you're writing on
                "hi",########################NEED TO CHANGE TO TROOP NUMBER FOR EACH TERRITORY             # name to draw
                (cx, cy-10),                # location (center of region) shifted to center text
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,                     # font scale
                (0, 255, 0),             # green text
                1,                       # thickness
                cv2.LINE_AA
            )           # image you're writing on

            

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