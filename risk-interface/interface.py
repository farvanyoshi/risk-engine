# Libraries
import tkinter as tk
from PIL import Image, ImageTk
import cv2
import numpy as np

# File Imports
import main




#Actual game

def gamespace():
    # Create the main window
    root = tk.Tk()
    root.state('zoomed')
    root.title("Risk Game")

    #creates risk background
    image_path = "riskmap_resized.jpg"
    original_image = Image.open(image_path)
    tk_image = ImageTk.PhotoImage(original_image)
    image_label = tk.Label(root, image=tk_image)
    image_label.image = tk_image
    image_label.pack(padx=5, pady=5)


    #Adds numbers to each region
    for 

    # Start the GUI event loop
    root.mainloop()

def on_space(event):
    #closes window and opens a new one
    root1.destroy()
    gamespace()


#open game start
root1 = tk.Tk()
root1.geometry("895x473")
root1.title("Risk Game")

#background image
image_path1 = "risk_background.jpg"
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





















# Create main window
root = tk.Tk()
root.title("Edge Region Labeler")
root.state("zoomed")

# Canvas to display image
canvas = tk.Label(root)
canvas.pack()

# Label to show number of regions
region_label = tk.Label(root, text="Detected Regions: 0", font=("Arial", 14))
region_label.pack(pady=5)

# Global variables
img_cv = None
regions = []

def open_image():

    global img_cv
    image_path = 'riskboard_resized.jpg'
    img_cv = cv2.imread(image_path)
    display_image(img_cv)
    region_label.config(text="Detected Regions: 0")  # Reset label

def display_image(img_cv):
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)
    img_tk = ImageTk.PhotoImage(img_pil)

    canvas.configure(image=img_tk)
    canvas.image = img_tk  # Keep reference

def detect_edges():
    global regions

    # Step 1: Convert to grayscale and detect edges
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    


    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.adaptiveThreshold(blurred, 255,
                              cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                              cv2.THRESH_BINARY_INV, 11, 2)
    
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)


    # Step 2: Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    regions = [cv2.approxPolyDP(cnt, 3, True) for cnt in contours]

    # Step 3: Create a labeled version of the edge image
    labeled_img = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

    for idx, contour in enumerate(regions):
        # Get center point of contour (via moments)
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            cv2.putText(labeled_img, str(idx + 1), (cx, cy),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        # Optionally draw the contour as well
            cv2.drawContours(labeled_img, [contour], -1, (255, 0, 0), 1)
    # Step 4: Display labeled image and update region count
    display_image(labeled_img)
    region_label.config(text=f"Detected Regions: {len(regions)}")

# Buttons
btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)

open_image()
detect_edges()

#assigned regions to territories

def on_click(event):
    #print(f"Mouse clicked at {event.x}, {event.y}")
    for i, region in enumerate(regions):
        region_num = i+1
        if cv2.pointPolygonTest(region, (event.x, event.y), False) >= 0:
            print(f"Clicked inside region {region_num}")
            if region_num == 163:
                region_name = "Alaska"
            elif region_num == 169:
                region_name = "Northwest Territory"
            elif region_num == 177:
                region_name = "Greenland"
            elif region_num == 178:
                pass #prevent double greenland repeat
            elif region_num == 140:
                region_name = "Alberta"
            elif region_num == 139:
                region_name = "Ontario"
            elif region_num == 143:
                region_name = "Quebec"
            elif region_num == 114:
                region_name = "Western United States"
            elif region_num == 112:
                region_name = "Eastern United States"
            elif region_num == 86:
                region_name = "Central America"
            elif region_num == 64:
                region_name = "Venezuela"
            elif region_num == 54:
                region_name = "Peru"
            elif region_num == 56:
                region_name = "Brazil"
            elif region_num == 25:
                region_name = "Argentina"
            elif region_num == 15:
                region_name = "South Africa"
            elif region_num == 9:
                region_name = "Madagascar"
            elif region_num == 29:
                region_name = "Congo"
            elif region_num == 49:
                region_name = "East Africa"
            elif region_num == 67:
                region_name = "North Africa"
            elif region_num == 61:
                region_name = "Egypt"
            elif region_num == 145:
                region_name = "Iceland"
            elif region_num == 127 or region_num == 130:
                region_name = "Great Britain"
            elif region_num == 95:
                region_name = "Western Europe"
            elif region_num == 94:
                region_name = "Southern Europe"
            elif region_num == 122:
                region_name = "Nothern Europe"
            elif region_num == 161:
                region_name = "Scandinavia"
            elif region_num == 160:
                region_name = "Ukraine"
            elif region_num == 78:
                region_name = "Middle East"
            elif region_num == 113:
                region_name = "Afghanistan"
            elif region_num == 83:
                region_name = "India"
            elif region_num == 167:
                region_name = "Ural"
            elif region_num == 175:
                region_name = "Siberia"
            elif region_num == 172:
                region_name = "Yakutsk"
            elif region_num == 144:
                region_name = "Irkutsk"
            elif region_num == 168:
                region_name = "Kamchatka"
            elif region_num == 120:
                region_name = "Japan"
            elif region_num == 118:
                region_name = "Mongolia"
            elif region_num == 107:
                region_name = "China"
            elif region_num == 69:
                region_name = "Siam"
            elif region_num == 28 or region_num == 36 or region_num == 27 or region_num == 17 or region_num == 20:
                region_name = "Indonesia"
            elif region_num == 43 or region_num == 44:
                region_name = "New Guinea"
            elif region_num ==  14:
                region_name = "Western Australia"
            elif region_num == 21:
                region_name = "Eastern Australia"
            elif region_num == 176:
                pass #prevent not a region error
            else:
                print("Not a Region")
                    
    print(region_name)

canvas.bind("<Button-1>", on_click)

root.mainloop()






