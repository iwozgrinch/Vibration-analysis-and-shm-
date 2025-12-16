import pandas as pd
import numpy as np
import os
import sys

# --- CONFIGURATION (EDIT THIS) ---

# 1. INPUT FILE PATH
# This should be the CSV file created by the vision_tracker.py script
INPUT_CSV_PATH = r"C:\Users\harin\Desktop\sem1\EL\data\raw_pixel_positions1.csv"

# 2. OUTPUT FILE PATH
# This is where the final, processed data (in millimeters) will be saved
OUTPUT_CSV_PATH = r"C:\Users\harin\Desktop\sem1\EL\data\processed_vibration_data.csv"

# 3. CALIBRATION CONSTANTS (***UPDATE THESE VALUES***)

# The known physical distance (in millimeters) you measured between the two clicked points.
# Example: If you clicked the 10mm mark and the 20mm mark, this value is 10.0.
KNOWN_PHYSICAL_DISTANCE_MM = 10.0 

# The pixel distance (D_px) that the calibration_finder.py script outputted.
# Example: 35.75
MEASURED_PIXEL_DISTANCE = 750.05 # <<< PASTE YOUR D_px VALUE HERE!

# --- MAIN CONVERSION LOGIC ---

def process_data_and_calibrate(input_path, output_path, known_mm, measured_px):
    """
    Loads raw pixel data, calculates the conversion factor, converts displacement 
    to millimeters, centers the data around zero, and saves the final result.
    """
    
    # 1. Check Input File
    if not os.path.exists(input_path):
        print(f"FATAL ERROR: Input file not found at: {input_path}")
        print("Please ensure vision_tracker.py was run successfully and the path is correct.")
        sys.exit(1)
        
    df = pd.read_csv(input_path)
    
    # 2. Calculate the Conversion Factor
    # Factor is MM per Pixel: (Known MM) / (Measured Pixels)
    MM_PER_PIXEL_FACTOR = known_mm / measured_px
    print(f"\nCalculated Calibration Factor: {MM_PER_PIXEL_FACTOR:.4f} mm per pixel")

    # 3. Determine the Baseline (Zero-point)
    # We use the mean of the first 50 frames to establish the stationary zero position.
    baseline_M1 = df['y_pixel_M1'].head(50).mean()
    baseline_M2 = df['y_pixel_M2'].head(50).mean()
    print(f"Baseline M1 (Average Y-Pixel): {baseline_M1:.2f} px")
    print(f"Baseline M2 (Average Y-Pixel): {baseline_M2:.2f} px")
    
    # 4. Convert Pixel Displacement to Millimeters
    
    # Note: Subtracting the baseline (mean position) from the raw pixel data centers 
    # the motion around the mean (y=0), giving us relative displacement in pixels.
    
    # Calculate relative displacement in pixels
    df['displacement_M1_px'] = df['y_pixel_M1'] - baseline_M1
    df['displacement_M2_px'] = df['y_pixel_M2'] - baseline_M2

    # Apply the conversion factor to get displacement in millimeters (mm)
    df['displacement_M1_mm'] = df['displacement_M1_px'] * MM_PER_PIXEL_FACTOR
    df['displacement_M2_mm'] = df['displacement_M2_px'] * MM_PER_PIXEL_FACTOR
    
    # 5. Prepare Output DataFrame (Select only necessary columns)
    output_df = df[['time_s', 'displacement_M1_mm', 'displacement_M2_mm']].copy()
    
    # 6. Save the Final Processed Data
    output_df.to_csv(output_path, index=False)
    
    print("\n--- Data Conversion Complete ---")
    print(f"Data saved to: {output_path}")
    print(f"First 5 displacement values (M1):")
    print(output_df['displacement_M1_mm'].head())
    print("\nThis CSV is now ready for plotting and Frequency Analysis (FFT).")


if __name__ == "__main__":
    if not os.path.exists('data'):
        os.makedirs('data')
        
    # Ensure the user has updated the calibration constants
    if MEASURED_PIXEL_DISTANCE == 35.75 and KNOWN_PHYSICAL_DISTANCE_MM == 10.0:
        print("\n*** WARNING ***: Please update the 'MEASURED_PIXEL_DISTANCE' and 'KNOWN_PHYSICAL_DISTANCE_MM' variables in the script.")
        print("Using placeholder values now. Data will be meaningless until corrected.")
        
    process_data_and_calibrate(
        INPUT_CSV_PATH, 
        OUTPUT_CSV_PATH, 
        KNOWN_PHYSICAL_DISTANCE_MM, 
        MEASURED_PIXEL_DISTANCE
    )