import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import os
import sys

# --- CONFIGURATION (EDIT THIS) ---

# 1. INPUT FILE PATH
# The processed data file (in millimeters) from calibration_converter.py
INPUT_CSV_PATH = 'data/processed_vibration_data.csv'

# 2. MARKER SELECTION
# Choose which marker to analyze for damping calculation
TARGET_COLUMN = 'displacement_M1_mm' 

# 3. ANALYSIS SETTINGS
# Number of samples (data points) to skip at the beginning of the analysis.
# We skip the initial impact/transient.
SKIP_INITIAL_SAMPLES = 100 

# --- CORE FUNCTIONS ---

def calculate_logarithmic_decrement(y_data, time_data, target_frequency_Hz):
    """
    Calculates damping ratio (zeta) using the Logarithmic Decrement method.
    It automatically finds the peak amplitudes in the signal decay.
    """
    
    # 1. Peak Detection
    # Estimate the distance between peaks using the calculated natural frequency (f_n).
    # Distance in samples = Fs / f_n
    
    T_avg = np.mean(np.diff(time_data))
    Fs = 1.0 / T_avg
    
    # The minimum distance between two peaks should be roughly one period
    distance_in_samples = int(Fs / target_frequency_Hz)
    
    # Find positive peaks (crests)
    peaks_indices, _ = find_peaks(y_data, distance=distance_in_samples * 0.8)
    
    if len(peaks_indices) < 3:
        print("\nFATAL ERROR in Damping Calculation: Fewer than 3 peaks found.")
        print("Please adjust SKIP_INITIAL_SAMPLES or check your data quality.")
        return None, None

    # 2. Selection for Log Decrement
    # Use the first peak (A1) and the last available peak (A_k) for stability.
    A1_index = peaks_indices[0]
    Ak_index = peaks_indices[-1]
    
    A1 = y_data[A1_index]
    Ak = y_data[Ak_index]
    
    k = len(peaks_indices) - 1 # Number of cycles between A1 and Ak

    # 3. Calculation
    
    # Logarithmic Decrement (delta)
    delta = (1 / k) * np.log(A1 / Ak)
    
    # Damping Ratio (zeta)
    zeta = delta / np.sqrt((2 * np.pi)**2 + delta**2)

    return zeta, (A1_index, Ak_index, k, A1, Ak)

def analyze_damping(input_path, target_column, skip_samples):
    """
    Main function to load data, prepare, calculate damping, and plot decay.
    """
    if not os.path.exists(input_path):
        print(f"FATAL ERROR: Processed data file not found at: {input_path}")
        sys.exit(1)
        
    df = pd.read_csv(input_path)
    
    # Get the data after skipping initial samples
    time_s = df['time_s'].values[skip_samples:]
    displacement_mm = df[target_column].values[skip_samples:]

    if len(displacement_mm) == 0:
        print("Error: Dataset is empty after skipping initial samples.")
        return
        
    # --- IMPORTANT ASSUMPTION ---
    # To find peaks automatically, we need the approximate natural frequency (f_n) 
    # which you found in Step 4. If you know the value, replace 5.0 with your f_n!
    
    # If the user did not run vibration_analyzer.py yet, we default to 5.0 Hz
    # USER TIP: Replace 5.0 with the f_n you found in Step 4 for better accuracy!
    APPROX_NATURAL_FREQUENCY_HZ = 5.0 

    zeta, decay_data = calculate_logarithmic_decrement(
        displacement_mm, 
        time_s, 
        APPROX_NATURAL_FREQUENCY_HZ
    )
    
    if zeta is None:
        return

    A1_idx, Ak_idx, k, A1, Ak = decay_data

    # --- Print Results ---
    print(f"\n--- Damping Analysis Results ({target_column}) ---")
    print(f"Cycles used for decay (k): {k}")
    print(f"Initial Peak Amplitude (A1): {A1:.4f} mm")
    print(f"Final Peak Amplitude (A{k+1}): {Ak:.4f} mm")
    print(f"Calculated Logarithmic Decrement (delta): {delta:.4f}")
    print(f"Calculated Damping Ratio (zeta, \u03B6): {zeta:.4f}")

    # --- Plotting Decay Curve ---
    plt.figure(figsize=(10, 6))
    plt.plot(time_s, displacement_mm, label='Decay Signal', linewidth=1.0)
    
    # Highlight the peaks used for calculation
    plt.plot(time_s[A1_idx], A1, 'o', color='green', markersize=8, label=f'Peak A1 ({A1:.2f} mm)')
    plt.plot(time_s[Ak_idx], Ak, 'o', color='red', markersize=8, label=f'Peak A{k+1} ({Ak:.2f} mm)')
    
    plt.title(f'Vibration Decay and Logarithmic Decrement - Damping Ratio $\\zeta = {zeta:.4f}$')
    plt.xlabel('Time (s)')
    plt.ylabel('Displacement (mm)')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    plt.show()


if __name__ == "__main__":
    analyze_damping(
        INPUT_CSV_PATH, 
        TARGET_COLUMN, 
        SKIP_INITIAL_SAMPLES
    )