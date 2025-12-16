import cv2
import numpy as np
import os 
import sys 

# --- CONFIGURATION (EDIT THIS) ---
# Change this to the exact path of your video file. 
# ***CRITICAL: Ensure this matches the video you used for the tracking script.***
VIDEO_PATH = r"C:\Users\harin\Desktop\sem1\EL\data\VIDEO2.mp4"

# Global list to store the coordinates of the two clicks
points = []

# Mouse callback function: This runs every time a mouse event happens
def click_event(event, x, y, flags, param):
    global points
    global img 

    # Check if the event was a left mouse button click
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(points) < 2:
            # 1. Store the coordinates (x, y)
            points.append((x, y))
            
            # 2. Draw the point on the image for visual confirmation
            cv2.circle(img, (x, y), 5, (0, 0, 255), -1)
            cv2.imshow('Calibration Frame', img)

            # 3. Once two points are recorded, calculate and print the distance
            if len(points) == 2:
                x1, y1 = points[0]
                x2, y2 = points[1]
                
                # Calculate the Euclidean distance (the pixel distance D_px)
                D_px = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                
                print("\n--- Calibration Measurement Complete ---")
                print(f"Point 1 (x1, y1): ({x1}, {y1})")
                print(f"Point 2 (x2, y2): ({x2}, {y2})")
                print(f"Measured Pixel Distance (D_px): {D_px:.2f} pixels")
                print("\nUSE THIS D_px VALUE to update 'MEASURED_PIXEL_DISTANCE' in calibration_converter.py")
                print("--- PRESS ANY KEY TO CLOSE WINDOWS ---")

# --- Main Script Execution ---

if __name__ == "__main__":
    # Robust check to ensure the video file exists before trying to open it
    if not os.path.exists(VIDEO_PATH):
        print(f"\nFATAL ERROR: Video file not found at the specified path.")
        print(f"Path configured: {VIDEO_PATH}")
        print("Please check the VIDEO_PATH variable in the script.")
        sys.exit(1)

    cap = cv2.VideoCapture(VIDEO_PATH)

    if not cap.isOpened():
        print(f"Error: Could not open video file at {VIDEO_PATH}. File might be corrupted or an unsupported format.")
        exit()

    ret, img = cap.read() # Read the first frame into the variable 'img'
    cap.release() 

    if ret:
        cv2.namedWindow('Calibration Frame')
        cv2.setMouseCallback('Calibration Frame', click_event)
        
        print("INSTRUCTIONS:")
        print("1. Click on the FIRST point on your ruler (e.g., the 10 mm mark).")
        print("2. Click on the SECOND point (e.g., the 20 mm mark, or 10 mm away from the first).")
        print("3. The pixel distance (D_px) will print in the console.")
        
        cv2.imshow('Calibration Frame', img)
        
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("Error: Could not read a frame from the video. Check if the video is empty.")