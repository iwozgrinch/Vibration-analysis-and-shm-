

import cv2

# IMPORTANT: Change this to the exact location and name of your calibration video file.
# Using r'...' helps handle Windows file paths (e.g., C:\Users\YourName\...)
VIDEO_PATH = r'cal_video.mp4' 

# 1. Create a video capture object
cap = cv2.VideoCapture(VIDEO_PATH)

# Check if the video file was successfully opened
if not cap.isOpened():
    # If the file couldn't be opened, print the error and stop the program
    print(f"Error: Could not open video file at {VIDEO_PATH}")
    # The 'exit()' command is often useful in scripts for clean termination
    exit()

# 2. Read the very first frame
ret, frame = cap.read()

# 3. If the read was successful (ret is True)
if ret:
    # Display the frame in a window named 'Calibration Frame'
    cv2.imshow('Calibration Frame', frame)
    
    # Wait indefinitely for a key press. This stops the script from closing immediately.
    # 0 means wait forever; any positive number is milliseconds.
    cv2.waitKey(0)
    
    # Close all OpenCV windows
    cv2.destroyAllWindows()
else:
    # Handle the case where the file opened but no frames could be read
    print("Error: Could not read a frame from the video. The file might be corrupted.")

# 4. Release the capture object to free up resources
cap.release()
>>> [DEBUG ON]
>>> [DEBUG OFF]
