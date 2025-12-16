Python 3.13.9 (tags/v3.13.9:8183fa5, Oct 14 2025, 14:09:13) [MSC v.1944 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
import cv2

import numpy as np

# Change this to the path of your calibration video file
VIDEO_PATH = r'cal_video.mp4' 

# Global list to store the coordinates of the two clicks
points = []

# Mouse callback function: This runs every time a mouse event happens
def click_event(event, x, y, flags, param):
    global points

    # Check if the event was a left mouse button click
    if event == cv2.EVENT_LBUTTONDOWN:
        # 1. Store the coordinates (x, y)
        points.append((x, y))
        
        # 2. Draw the point on the image for visual confirmation
        cv2.circle(img, (x, y), 5, (0, 0, 255), -1)
        cv2.imshow('Calibration Frame', img)

        # 3. Once two points are recorded, calculate and print the distance
        if len(points) == 2:
            # Unpack the two coordinate pairs
...             x1, y1 = points[0]
...             x2, y2 = points[1]
... 
...             # Calculate the Euclidean distance (the pixel distance D_px)
...             D_px = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
... 
...             print("---")
...             print(f"Point 1 (x1, y1): ({x1}, {y1})")
...             print(f"Point 2 (x2, y2): ({x2}, {y2})")
...             print(f"Measured Pixel Distance (D_px): {D_px:.2f} pixels")
...             print("--- PRESS ANY KEY TO CLOSE WINDOWS ---")
... 
...             # Reset points list for safety (optional)
...             # points = [] 
... 
... 
... # --- Main Script Execution ---
... 
... cap = cv2.VideoCapture(VIDEO_PATH)
... 
... if not cap.isOpened():
...     print(f"Error: Could not open video file at {VIDEO_PATH}")
...     exit()
... 
... ret, img = cap.read() # Read the first frame into the variable 'img'
... 
... if ret:
...     # Set the function to be called on mouse events
...     cv2.namedWindow('Calibration Frame')
...     cv2.setMouseCallback('Calibration Frame', click_event)
...     
...     # Show the image and wait for the user to click
...     print("Click on the FIRST point on your ruler (e.g., the 5 mm mark).")
...     print("Then, click on the SECOND point (e.g., the 15 mm mark).")
...     cv2.imshow('Calibration Frame', img)
...     
...     cv2.waitKey(0)
...     cv2.destroyAllWindows()
... else:
...     print("Error: Could not read a frame from the video.")
... 
