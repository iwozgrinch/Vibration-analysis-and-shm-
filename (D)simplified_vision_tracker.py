import cv2
import numpy as np
import pandas as pd
import os

# --- CONFIGURATION (EDIT THIS) ---
# UPDATE THIS with the path to your video file (MP4, AVI, etc.)
VIDEO_PATH = r"C:\Users\harin\Desktop\sem1\EL\data\VIDEO2.mp4"
# UPDATE THIS with the desired output CSV file path
OUTPUT_CSV_PATH =  r"C:\Users\harin\Desktop\sem1\EL\data\raw_pixel_positions1.csv"
# NEW: Set the Frame Rate (Frames Per Second) of your video camera!
VIDEO_FRAME_RATE = 90.0 # <--- Set this to your camera's FPS (e.g., 30.0, 60.0, 120.0)

# --- MAIN FUNCTIONS ---

def track_markers(video_path, output_csv_path):
    """
    Initializes two CSRT trackers, tracks two markers (M1 & M2) frame-by-frame,
    and saves the raw center Y-pixel positions and time to a CSV file.
    """
    
    # Check if the video file exists before loading
    if not os.path.exists(video_path):
        print(f"FATAL ERROR: Video file not found at: {video_path}")
        print("Please update the VIDEO_PATH variable in the script.")
        return

    print(f"Loading video from: {video_path}")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video at {video_path}")
        return

    # 1. READ FIRST FRAME & INITIALIZE
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read first frame.")
        return

    # --- Marker Initialization ---
    trackers = []
    
    # --- Marker 1 (Center Span) Selection ---
    print("\n--- Marker 1 (Center Span) Setup ---")
    print("Draw a tight bounding box around the center marker and press ENTER/SPACE.")
    roi1 = cv2.selectROI("Select Marker 1 ROI (Center Span)", frame, False)
    
    # Initialize and start Tracker 1
    tracker1 = cv2.TrackerCSRT_create()
    tracker1.init(frame, roi1)
    trackers.append(tracker1)
    
    # --- Marker 2 (Quarter Span) Selection ---
    print("\n--- Marker 2 (Quarter Span) Setup ---")
    print("Draw a tight bounding box around the quarter-span marker and press ENTER/SPACE.")
    roi2 = cv2.selectROI("Select Marker 2 ROI (Quarter Span)", frame, False)
    
    # Initialize and start Tracker 2
    tracker2 = cv2.TrackerCSRT_create()
    tracker2.init(frame, roi2)
    trackers.append(tracker2)
    
    cv2.destroyAllWindows()
    
    # UPDATED: Added 'time_s' column
    data = {'frame_index': [], 'time_s': [], 'y_pixel_M1': [], 'y_pixel_M2': []}
    frame_count = 0

    # 2. TRACKING LOOP
    print("\nStarting frame-by-frame tracking... Press 'q' to stop early.")
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Manually update each tracker sequentially
        success1, box1 = trackers[0].update(frame)
        success2, box2 = trackers[1].update(frame)
        
        success = success1 and success2 # Overall success is only true if both succeed

        if success:
            # Calculate current time
            current_time = frame_count / VIDEO_FRAME_RATE
            
            # Extract data from Tracker 1 (M1)
            x1, y1, w1, h1 = [int(v) for v in box1]
            y_center_M1 = y1 + h1 // 2
            
            # Extract data from Tracker 2 (M2)
            x2, y2, w2, h2 = [int(v) for v in box2]
            y_center_M2 = y2 + h2 // 2
            
            # Store the data
            data['frame_index'].append(frame_count)
            data['time_s'].append(current_time) # Store time in seconds
            data['y_pixel_M1'].append(y_center_M1)
            data['y_pixel_M2'].append(y_center_M2)
            
            # Optional: Visualization feedback
            cv2.rectangle(frame, (x1, y1), (x1 + w1, y1 + h1), (255, 0, 0), 2)
            cv2.rectangle(frame, (x2, y2), (x2 + w2, y2 + h2), (0, 0, 255), 2)
            cv2.putText(frame, f"Time: {current_time:.2f}s | Frame: {frame_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        else:
            cv2.putText(frame, "Tracking Failed!", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.imshow("Tracking Markers", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        frame_count += 1
        
    # 3. FINALIZATION AND SAVING
    cap.release()
    cv2.destroyAllWindows()
    
    # Only save if we captured some data
    if data['frame_index']:
        df = pd.DataFrame(data)
        df.to_csv(output_csv_path, index=False)
        
        print("\n--- Tracking Complete ---")
        print(f"Total frames processed: {frame_count}")
        print(f"Data sampling rate: {VIDEO_FRAME_RATE} Hz")
        print(f"Raw pixel data saved to: {output_csv_path}")
    else:
        print("\n--- Tracking Aborted ---")
        print("No data was saved because tracking failed or was stopped early.")


if __name__ == "__main__":
    if not os.path.exists('data'):
        os.makedirs('data')
    track_markers(VIDEO_PATH, OUTPUT_CSV_PATH)