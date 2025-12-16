import pandas as pd
import numpy as np
from scipy.fft import fft, fftfreq
import os
import sys

# --- CONFIGURATION (EDIT THIS) ---

# 1. INPUT FILE PATH
# The processed data file (in millimeters) from calibration_converter.py
INPUT_CSV_PATH = 'data/processed_vibration_data.csv'

# 2. ANALYSIS SETTINGS
# Number of samples (data points) to skip at the beginning of the analysis.
SKIP_INITIAL_SAMPLES = 50 

# 3. KNOWN NATURAL FREQUENCY (Crucial for accuracy!)
# Use the f_n value you found in Step 4 (vibration_analyzer.py)
# Example: if f_n was 4.87 Hz, use that value here.
DOMINANT_FREQUENCY_HZ = 4.87 # <<< UPDATE THIS WITH YOUR ACTUAL f_n

# --- MAIN ANALYSIS LOGIC ---

def analyze_mode_shape(input_path, skip_samples, target_fn):
    """
    Loads processed data and calculates the relative phase difference between
    Marker 1 (M1) and Marker 2 (M2) at the natural frequency.
    """
    
    # 1. Check Input File
    if not os.path.exists(input_path):
        print(f"FATAL ERROR: Processed data file not found at: {input_path}")
        sys.exit(1)
        
    df = pd.read_csv(input_path)
    
    # 2. Prepare Data for Analysis
    time_s = df['time_s'].values[skip_samples:]
    disp_M1 = df['displacement_M1_mm'].values[skip_samples:]
    disp_M2 = df['displacement_M2_mm'].values[skip_samples:]

    N = len(disp_M1) 
    
    # Calculate the Sample Rate (Fs) and Time Step (T)
    T = np.mean(np.diff(time_s)) 
    Fs = 1.0 / T 
    xf = fftfreq(N, T) # Frequencies

    print(f"\n--- Mode Shape Analysis Parameters ---")
    print(f"Target Frequency (f_n): {target_fn:.3f} Hz")
    
    # 3. Perform Fast Fourier Transform (FFT) on both signals
    yf_M1 = fft(disp_M1)
    yf_M2 = fft(disp_M2)

    # 4. Find the Frequency Index
    # Locate the index in the frequency array (xf) that is closest to our target f_n
    idx = np.argmin(np.abs(xf - target_fn))
    
    # 5. Extract Complex Magnitudes at f_n
    # The complex number at this index holds both amplitude and phase information.
    complex_M1 = yf_M1[idx]
    complex_M2 = yf_M2[idx]

    # 6. Calculate Phase (Angle)
    # The phase is the angle of the complex number in radians.
    phase_M1_rad = np.angle(complex_M1)
    phase_M2_rad = np.angle(complex_M2)
    
    # Convert to degrees
    phase_M1_deg = np.degrees(phase_M1_rad)
    phase_M2_deg = np.degrees(phase_M2_rad)

    # 7. Calculate Relative Phase Difference
    # The relative phase tells us if the two markers are moving in sync or opposition.
    relative_phase_deg = np.abs(phase_M1_deg - phase_M2_deg)
    
    # Normalize the difference to be between 0 and 180 degrees
    if relative_phase_deg > 180:
        relative_phase_deg = 360 - relative_phase_deg

    # 8. Determine Mode Shape
    if relative_phase_deg < 45:
        mode = "1st Bending Mode (Fundamental Mode)"
        description = "Both markers are moving in the same direction (in-phase)."
    elif relative_phase_deg > 135:
        mode = "2nd Bending Mode (Higher Harmonic)"
        description = "Markers are moving in opposite directions (out-of-phase)."
    else:
        mode = "Uncertain or Mixed Mode"
        description = "The relative phase is ambiguous, suggesting complex motion or noise."
        
    # --- Print Results ---
    print("\n--- Mode Shape Analysis Complete ---")
    print(f"Phase M1 at {target_fn:.3f} Hz: {phase_M1_deg:.2f}°")
    print(f"Phase M2 at {target_fn:.3f} Hz: {phase_M2_deg:.2f}°")
    print(f"\nCalculated Relative Phase Difference: {relative_phase_deg:.2f}°")
    print(f"Identified Mode Shape: {mode}")
    print(f"Description: {description}")


if __name__ == "__main__":
    analyze_mode_shape(
        INPUT_CSV_PATH, 
        SKIP_INITIAL_SAMPLES, 
        DOMINANT_FREQUENCY_HZ
    )