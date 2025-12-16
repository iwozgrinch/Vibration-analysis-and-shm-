Python 3.13.9 (tags/v3.13.9:8183fa5, Oct 14 2025, 14:09:13) [MSC v.1944 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter

# Define the paths for your processed data files
VIDEO_DATA_PATH = 'real_displacement.csv' # Output from Step 3.2 (Time vs. Displacement in mm)
REF_DATA_PATH = 'accel_data.csv'         # Input from Phase I (Reference Accelerometer Data)

# --- FFT Analysis Function ---
def perform_fft(time_data, signal_data, sample_rate, title):
    """
    Performs FFT on a signal and plots the frequency spectrum.
    """
    N = len(signal_data) # Total number of data points
    
    # Detrend the signal (removes mean/DC offset)
    detrended_signal = signal_data - np.mean(signal_data)
    
    # Compute the FFT
    Y = np.fft.fft(detrended_signal)
    
    # Calculate the corresponding frequencies
    T = 1.0 / sample_rate
    xf = np.fft.fftfreq(N, T)[:N//2]
    
    # Calculate the magnitude (Amplitude Spectrum) and take the first half
    # (since the FFT result is symmetric)
    yf = 2.0/N * np.abs(Y[0:N//2])

    # Find the dominant frequency (excluding the DC component at 0 Hz)
    dominant_freq_index = np.argmax(yf[1:]) + 1
    dominant_frequency = xf[dominant_freq_index]
    
    print(f"Dominant Frequency for {title}: {dominant_frequency:.2f} Hz")

    # Plotting the result
    plt.figure(figsize=(10, 4))
    plt.plot(xf, yf)
    plt.title(f'Frequency Spectrum - {title}')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Amplitude')
    plt.grid(True)
    plt.xlim(0, 50) # Typically, vibration analysis focuses on lower frequencies
    plt.tight_layout()
    
    return dominant_frequency

# --- Main Execution ---
... 
... # 1. Load the Video-Derived Data
... try:
...     df_video = pd.read_csv(VIDEO_DATA_PATH)
...     video_time = df_video['Time'].values
...     video_signal = df_video['Displacement_mm'].values
...     
...     # Calculate Sample Rate (Fs) from the data
...     # We assume time steps are uniform for a clean FFT
...     SAMPLE_RATE_VIDEO = 1.0 / np.mean(np.diff(video_time))
...     print(f"Video Sample Rate: {SAMPLE_RATE_VIDEO:.2f} Hz")
...     
...     # Perform FFT on Video Data
...     video_freq = perform_fft(video_time, video_signal, SAMPLE_RATE_VIDEO, 'Video-Derived Displacement (mm)')
... 
... except FileNotFoundError:
...     print(f"Error: Video data file not found at {VIDEO_DATA_PATH}. Run Step 3.2 first.")
... 
... # 2. Load the Reference Data
... try:
...     df_ref = pd.read_csv(REF_DATA_PATH)
...     ref_time = df_ref['Time'].values
...     ref_signal = df_ref['Acceleration'].values # Assuming column name is 'Acceleration'
...     
...     # Calculate Sample Rate (Fs) for Reference Data
...     SAMPLE_RATE_REF = 1.0 / np.mean(np.diff(ref_time))
...     print(f"Reference Sample Rate: {SAMPLE_RATE_REF:.2f} Hz")
...     
...     # Perform FFT on Reference Data
...     ref_freq = perform_fft(ref_time, ref_signal, SAMPLE_RATE_REF, 'Reference Accelerometer Data (Acceleration)')
... 
... except FileNotFoundError:
...     print(f"Error: Reference data file not found at {REF_DATA_PATH}. Run Phase I setup first.")
... 
... # Show all generated plots
