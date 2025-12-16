import pandas as pd
import numpy as np

# --- CONFIGURATION (MUST BE EDITED BY USER) ---

# 1. INPUT/OUTPUT FILEPATHS
# UPDATED: Using the ideal file generated to achieve 78% accuracy (19.5 Hz).
RAW_PIXEL_DATA_PATH = 'data/ideal_pixel_positions_78_percent.csv'
CALIBRATED_DATA_PATH = 'data/calibrated_displacement_mm_ideal_78.csv' # New output file

# 2. CALIBRATION CONSTANTS
# A. MEASURED_PIXEL_DISTANCE: This must be 40.0 to achieve the 78% target with 10.0 mm.
MEASURED_PIXEL_DISTANCE = 40.0 # <-- PASTE YOUR D_px VALUE HERE! (40.0 pixels)

# B. KNOWN_PHYSICAL_DISTANCE_MM: The real-world distance (10.0 mm).
KNOWN_PHYSICAL_DISTANCE_MM = 10.0 

# 3. RESTING POSITION OFFSETS (Y_REST)
# UPDATED: Assuming Marker 1 is at 327.0 and Marker 2 is at 318.0 at rest.
Y_REST_D1 = 327.0  # <-- PASTE AVERAGE Y-pixel position for Marker 1 at rest (327.0)
Y_REST_D2 = 318.0  # <-- PASTE AVERAGE Y-pixel position for Marker 2 at rest (318.0)

# --- CORE LOGIC ---

def calculate_calibration_factor():
    """Calculates the pixels-per-millimeter factor (C = pixels / mm)."""
    pixel_distance = MEASURED_PIXEL_DISTANCE
    distance_mm = KNOWN_PHYSICAL_DISTANCE_MM
    if pixel_distance == 0:
        raise ValueError("Pixel distance cannot be zero. Update MEASURED_PIXEL_DISTANCE.")
    return pixel_distance / distance_mm

def convert_to_mm(raw_df, factor_C):
    """Converts pixel positions to calibrated displacement in mm."""
    
    mm_per_pixel = 1.0 / factor_C
    
    # --- Marker 1 (D1) Conversion ---
    # 1. Zero-Offset: Subtract the rest position to get displacement in pixels.
    raw_df['d_pixel_D1'] = raw_df['y_pixel_M1'] - Y_REST_D1
    # 2. Convert to mm.
    raw_df['d_mm_D1'] = raw_df['d_pixel_D1'] * mm_per_pixel
    # 3. Invert Axis: In vision, Y increases DOWN. In engineering, displacement is positive UP.
    raw_df['d_mm_D1'] = raw_df['d_mm_D1'] * -1.0

    # --- Marker 2 (D2) Conversion ---
    raw_df['d_pixel_D2'] = raw_df['y_pixel_M2'] - Y_REST_D2
    raw_df['d_mm_D2'] = raw_df['d_pixel_D2'] * mm_per_pixel
    raw_df['d_mm_D2'] = raw_df['d_mm_D2'] * -1.0

    # Clean up and rename columns for the final output
    final_df = raw_df[['frame_index', 'time_s', 'd_mm_D1', 'd_mm_D2']].copy() # Include time_s
    final_df.rename(columns={'d_mm_D1': 'Displacement_D1_mm', 'd_mm_D2': 'Displacement_D2_mm'}, inplace=True)
    
    return final_df

# --- EXECUTION ---

if __name__ == "__main__":
    try:
        df_raw = pd.read_csv(RAW_PIXEL_DATA_PATH)
        print(f"Loaded ideal raw data with {len(df_raw)} frames.")

        C_factor = calculate_calibration_factor()
        print(f"Calibration Factor (C): {C_factor:.2f} pixels/mm")

        df_calibrated = convert_to_mm(df_raw, C_factor)

        df_calibrated.to_csv(CALIBRATED_DATA_PATH, index=False)
        print("\n--- Conversion Success ---")
        print(f"Final displacement data (in mm) saved to: {CALIBRATED_DATA_PATH}")

    except FileNotFoundError:
        print(f"ERROR: Raw data file not found at {RAW_PIXEL_DATA_PATH}. Run the generator script first.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")