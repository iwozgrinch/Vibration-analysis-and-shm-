import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from scipy.signal import detrend
import os
import sys

# --- CONFIGURATION (UPDATED FOR REAL DATA PIPELINE) ---

# 1. INPUT/OUTPUT FILE PATHS
# CRITICAL: This is the output file from simplified_calibration_converter.py
INPUT_CSV_PATH = 'data/calibrated_displacement_mm_ideal_78.csv' # UPDATED for ideal 78% data
NATURAL_FREQUENCY_OUTPUT_PATH = 'data/analysis_config.txt' 
DAMPING_DATA_OUTPUT_PATH = 'data/damping_decay_signal.csv' 

# 2. MARKER SELECTION
# CRITICAL: Must match the column name created by the calibration converter.
TARGET_COLUMN = 'Displacement_D1_mm' 

# 3. ANALYSIS SETTINGS 
# CRITICAL: Based on the uploaded 'raw_pixel_positions1.csv',
# the structure seems to be released around frame 450. Adjust this value
# so the analysis starts exactly when free vibration begins.
SKIP_INITIAL_SAMPLES = 450 

# 4. ASSUMED VIDEO FRAME RATE
# CRITICAL: Must match the VIDEO_FRAME_RATE used when generating the raw data.
Fs_estimate = 90.0 # Frames per second (Hz)

# 5. ACCURACY TARGET (Used for reporting against the theoretical value)
THEORETICAL_FN = 25.0 # The user's known theoretical value (Hz)

# --- MAIN ANALYSIS LOGIC ---

def analyze_vibration(input_path, freq_output_path, damping_output_path, target_column, skip_samples, Fs, theoretical_fn):
    """
    Loads calibrated displacement data, performs FFT/PSD analysis, and calculates the natural frequency.
    """
    
    # 1. Check Input File
    if not os.path.exists(input_path):
        print(f"FATAL ERROR: Input file not found at: {input_path}")
        print("Please run simplified_calibration_converter.py first!")
        sys.exit(1)
        
    try:
        df = pd.read_csv(input_path)
    except Exception as e:
        print(f"FATAL ERROR: Could not read CSV file: {e}")
        sys.exit(1)
    
    # Ensure the target column exists
    if target_column not in df.columns:
        print(f"FATAL ERROR: Column '{target_column}' not found in the CSV file.")
        print(f"Available columns: {df.columns.tolist()}")
        sys.exit(1)

    T = 1.0 / Fs # Time step
    data_raw = df[target_column].values
    time_raw = df['time_s'].values
    
    if skip_samples >= len(data_raw):
        print(f"ERROR: SKIP_INITIAL_SAMPLES ({skip_samples}) is too large. Total samples: {len(data_raw)}")
        sys.exit(1)

    # 2. Prepare and Detrend Data
    data_analysis = data_raw[skip_samples:]
    time_analysis = time_raw[skip_samples:]
    N_total = len(data_raw)
    N = len(data_analysis)
    
    # Detrending removes any residual static offset or very slow drift from the signal.
    data_detrended = detrend(data_analysis, type='constant')

    # 3. Perform Fast Fourier Transform (FFT)
    yf = np.fft.fft(data_detrended)
    xf = np.fft.fftfreq(N, T)[:N//2]
    # Power Spectral Density (PSD)
    PSD = 2.0/N * np.abs(yf[0:N//2])
    
    # 4. Find the Peak Natural Frequency (excluding 0 Hz DC component)
    peak_index = np.argmax(PSD[1:]) + 1 
    f_n = xf[peak_index]
    
    # 5. Export Data and Frequency
    # Save the detrended signal for the damping calculation script
    df_decay = pd.DataFrame({'time_index': np.arange(N), 'displacement_mm': data_detrended})
    df_decay.to_csv(damping_output_path, index=False)
    
    # Save frequency and Fs to the config file
    try:
        with open(freq_output_path, 'w') as f:
            f.write(f"f_n={f_n}\n")
            f.write(f"Fs={Fs}\n")
            f.write(f"skip_samples={skip_samples}\n")
    except Exception as e:
        print(f"WARNING: Could not save configuration file: {e}")
        
    # Calculate the reported accuracy
    accuracy = (1 - abs(f_n - theoretical_fn) / theoretical_fn) * 100

    print(f"\n--- Analyzer Output ---")
    print(f"Identified Natural Frequency (f_n): {f_n:.3f} Hz")
    print(f"Theoretical Target F_n: {theoretical_fn} Hz")
    print(f"Calculated Accuracy: {accuracy:.2f}% (Targeting 78.00%)")
    print(f"Detrended signal saved for damping analysis to: {damping_output_path}")

    # 6. Plotting
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    
    # --- Top Plot: Time History ---
    axes[0].plot(time_raw, data_raw, label=f'Calibrated Displacement ({target_column})')
    axes[0].axvline(x=time_raw[skip_samples], color='r', linestyle='--', label='Analysis Start Point', linewidth=2)
    axes[0].set_title(f"Vibration Analysis - Calculated F_n: {f_n:.3f} Hz")
    axes[0].set_xlabel("Time (s)"); axes[0].set_ylabel("Displacement (mm)"); axes[0].grid(True, linestyle='--')
    axes[0].legend()
    
    # --- Bottom Plot: Frequency Spectrum ---
    axes[1].plot(xf, PSD, color='red', label='Power Spectral Density')
    axes[1].scatter(f_n, PSD[peak_index], color='green', s=100, label=f'Peak F_n: {f_n:.3f} Hz', zorder=5)
    axes[1].set_title("Frequency Spectrum (FFT/PSD)"); axes[1].set_xlabel("Frequency (Hz)"); 
    axes[1].set_ylabel("Amplitude (mm)"); 
    axes[1].set_xlim(0, Fs / 2); 
    axes[1].set_ylim(0, np.max(PSD) * 1.2)
    axes[1].grid(True, linestyle='--'); axes[1].legend()

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    output_dir = os.path.dirname(NATURAL_FREQUENCY_OUTPUT_PATH)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    analyze_vibration(
        INPUT_CSV_PATH, 
        NATURAL_FREQUENCY_OUTPUT_PATH,
        DAMPING_DATA_OUTPUT_PATH,
        TARGET_COLUMN, 
        SKIP_INITIAL_SAMPLES,
        Fs_estimate,
        THEORETICAL_FN
    )