import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
import os
import sys

# --- CONFIGURATION (EDIT THIS) ---

# 1. INPUT FILE PATH
# This is the processed data file (in millimeters) created by calibration_converter.py
INPUT_CSV_PATH = r"C:\Users\harin\Desktop\sem1\EL\data\processed_vibration_data.csv"

# 2. MARKER SELECTION
# Choose which marker to analyze for the FFT (typically the center marker M1)
TARGET_COLUMN = 'displacement_M1_mm' 

# 3. ANALYSIS SETTINGS
# Number of samples (data points) to skip at the beginning of the analysis.
# Useful for skipping the initial transient or impact event.
SKIP_INITIAL_SAMPLES = 5 

# --- MAIN ANALYSIS LOGIC ---

def analyze_and_plot_vibration(input_path, target_column, skip_samples):
    """
    Loads processed data, performs FFT to find the natural frequency, 
    and generates time-domain and frequency-domain plots.
    """
    
    # 1. Check Input File
    if not os.path.exists(input_path):
        print(f"FATAL ERROR: Processed data file not found at: {input_path}")
        print("Please ensure calibration_converter.py was run successfully and the path is correct.")
        sys.exit(1)
        
    df = pd.read_csv(input_path)
    
    # 2. Prepare Data for Analysis
    # Get the time and displacement arrays, skipping the initial transient data
    time_s = df['time_s'].values[skip_samples:]
    displacement_mm = df[target_column].values[skip_samples:]

    if len(displacement_mm) == 0:
        print("Error: Dataset is empty after skipping initial samples.")
        return

    N = len(displacement_mm) # Number of data points used in the analysis
    
    # Calculate the Sample Rate (Fs) and Time Step (T)
    # The time step is the average difference between consecutive time points
    T = np.mean(np.diff(time_s)) 
    Fs = 1.0 / T # Sample Frequency (Hz)

    print(f"\n--- Analysis Parameters ---")
    print(f"Sampling Frequency (Fs): {Fs:.2f} Hz")
    print(f"Total Samples Analyzed (N): {N}")
    print(f"Total Time Analyzed: {time_s[-1] - time_s[0]:.2f} seconds")
    
    # 3. Perform Fast Fourier Transform (FFT)
    # yf: The magnitude of the FFT (complex numbers)
    # xf: The frequencies corresponding to the magnitudes
    
    yf = fft(displacement_mm)
    xf = fftfreq(N, T)[:N//2] # Only take the positive frequency side

    # Calculate the Power Spectral Density (PSD)
    # The magnitude squared gives a measure of power at each frequency
    # We only care about the positive frequency components
    psd = 2.0/N * np.abs(yf[0:N//2]) 

    # 4. Find the Dominant Natural Frequency
    # Find the index of the largest magnitude peak in the PSD
    peak_index = np.argmax(psd)
    natural_frequency_Hz = xf[peak_index]

    print(f"\n--- Results ---")
    print(f"Dominant Natural Frequency (f_n): {natural_frequency_Hz:.3f} Hz")
    print(f"Dominant Amplitude (Max PSD): {psd[peak_index]:.4f} mm")
    
    # 5. Plotting (Time Domain and Frequency Domain)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    fig.suptitle(f"Vision-Based Vibration Analysis - Marker: {target_column}", fontsize=16)

    # --- Plot 1: Time Domain (Displacement vs. Time) ---
    ax1.plot(time_s, displacement_mm, label='Displacement', linewidth=1.5)
    ax1.set_title('Displacement Time History')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Displacement (mm)')
    ax1.grid(True, linestyle='--', alpha=0.6)
    ax1.legend()
    
    # --- Plot 2: Frequency Domain (FFT/PSD) ---
    ax2.plot(xf, psd, label='Power Spectral Density', color='red', linewidth=2)
    
    # Highlight the dominant natural frequency peak
    ax2.plot(natural_frequency_Hz, psd[peak_index], 'o', color='green', markersize=8, 
             label=f'Peak f_n: {natural_frequency_Hz:.3f} Hz')
             
    ax2.set_title('Frequency Spectrum (FFT/PSD)')
    ax2.set_xlabel('Frequency (Hz)')
    ax2.set_ylabel('Amplitude (mm)')
    ax2.set_xlim(0, Fs / 2) # Limit x-axis to Nyquist frequency
    ax2.grid(True, linestyle='--', alpha=0.6)
    ax2.legend()

    plt.tight_layout(rect=[0, 0, 1, 0.96]) # Adjust layout to prevent title overlap
    plt.show()

if __name__ == "__main__":
    analyze_and_plot_vibration(
        INPUT_CSV_PATH, 
        TARGET_COLUMN, 
        SKIP_INITIAL_SAMPLES
    )