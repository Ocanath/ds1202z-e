import numpy as np
import matplotlib.pyplot as plt
import argparse
import scipy as scipy
from scipy.signal import find_peaks

def plot_from_file(filename):
    """Plot oscilloscope data from numpy .npz file"""
    data = np.load(filename)

    # Extract time and voltage data
    time = data['time']  # first array (time)
    ch1 = None
    ch2 = None
    if('channel_1' in data):
        ch1 = data['channel_1']  # second array (voltage)
    if('channel_2' in data):
        ch2 = data['channel_2']

    fig,ax = plt.subplots()
    if(ch1 is not None):
        ax.plot(time, ch1)
    if(ch2 is not None):
        ax.plot(time, ch2)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Voltage (V)')
    ax.set_title('Oscilloscope Data')
    ax.grid(True)
    

def plot_fft(filename, db_scale=False, find_peaks_n=None, max_freq=None):
    data = np.load(filename)
    time = data['time']

    # Get sampling parameters
    T = (time[len(time)-1] - time[0])	#duration
    fs = len(time)/T					#samples per second
    N = len(time)
    print(f"Using fs = {fs}")

    # Calculate frequency array (same for all channels)
    fft_freq = scipy.fft.fftfreq(N, 1/fs)
    positive_freq_idx = fft_freq > 0

    # Apply frequency limit if specified
    if max_freq is not None:
        freq_limit_idx = fft_freq <= max_freq
        positive_freq_idx = positive_freq_idx & freq_limit_idx

    fig, ax = plt.subplots()

    # Iterate through all available channel data
    channel_count = 0
    peak_info = []  # Store peak information for all channels

    for key in data.keys():
        if key.startswith('channel_'):
            channel_num = key.split('_')[1]
            channel_data = data[key]

            # Calculate FFT for this channel
            fft_values = scipy.fft.fft(channel_data)
            fft_magnitude = np.abs(fft_values) * 2 / N  # absolute value, and scale to volts

            # Get positive frequency data
            freq_khz = fft_freq[positive_freq_idx] * 1e-3
            mag_positive = fft_magnitude[positive_freq_idx]

            # Convert to dB scale if requested
            if db_scale:
                mag_plot = 20 * np.log10(np.maximum(mag_positive, 1e-10))  # Avoid log(0)
                ylabel = 'Magnitude (dB)'
                title_suffix = ' (dB Scale)'
            else:
                mag_plot = mag_positive
                ylabel = 'Magnitude (Volts)'
                title_suffix = ''

            # Plot positive frequencies only and capture the line object to get color
            line = ax.plot(freq_khz, mag_plot,
                          label=f'Channel {channel_num}',
                          linewidth=1)[0]

            # Get the color used for this channel's line
            channel_color = line.get_color()

            # Find peaks if requested
            if find_peaks_n is not None:
                peaks, properties = find_peaks(mag_positive, height=0)
                if len(peaks) > 0:
                    # Get the N largest peaks
                    peak_heights = mag_positive[peaks]
                    largest_peaks_idx = np.argsort(peak_heights)[-find_peaks_n:]
                    largest_peaks = peaks[largest_peaks_idx]

                    # Store peak information and add labels
                    for peak_idx in largest_peaks:
                        freq_peak = freq_khz[peak_idx]
                        mag_peak = mag_positive[peak_idx]
                        if db_scale:
                            mag_peak_display = 20 * np.log10(max(mag_peak, 1e-10))
                        else:
                            mag_peak_display = mag_peak
                        peak_info.append((channel_num, freq_peak, mag_peak, mag_peak_display))

                        # Mark peaks on plot with matching channel color
                        ax.plot(freq_peak, mag_peak_display, 'o',
                               color=channel_color, markersize=4)

                        # Add label near the peak
                        if db_scale:
                            label_text = f'{freq_peak:.1f}kHz\n{mag_peak_display:.1f}dB'
                        else:
                            label_text = f'{freq_peak:.1f}kHz\n{mag_peak_display:.3f}V'

                        ax.annotate(label_text, (freq_peak, mag_peak_display),
                                   xytext=(5, 5), textcoords='offset points',
                                   fontsize=8, ha='left',
                                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))

            channel_count += 1

    ax.set_xlabel('Frequency (kHz)')
    ax.set_ylabel(ylabel)
    ax.set_title(f'FFT Magnitude Spectrum{title_suffix}')
    ax.grid(True)

    # Add legend if multiple channels
    if channel_count > 1:
        ax.legend()

    # Display peak information
    if find_peaks_n is not None and peak_info:
        print("\n=== Peak Analysis ===")
        peak_info.sort(key=lambda x: x[2], reverse=True)  # Sort by magnitude
        for i, (ch, freq, mag_v, mag_display) in enumerate(peak_info[:find_peaks_n * channel_count]):
            if db_scale:
                print(f"Peak {i+1}: Ch{ch} @ {freq:.2f} kHz, {mag_display:.1f} dB ({mag_v:.4f} V)")
            else:
                print(f"Peak {i+1}: Ch{ch} @ {freq:.2f} kHz, {mag_display:.4f} V")

        # Peak info is now displayed directly on the plot near each peak

    
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot oscilloscope data from numpy file')
    parser.add_argument('filename', help='Path to the .npz data file')
    parser.add_argument('--fft', action='store_true', help="Flag to enable fft. If enabled, a second plot will be generated showing the magnitude spectrum FFT of the data")
    parser.add_argument('--db', action='store_true', help="Plot FFT magnitude in dB scale (only with --fft)")
    parser.add_argument('--findpeaks', type=int, metavar='N', help="Find and display N largest peaks per channel (only with --fft)")
    parser.add_argument('--maxfreq', type=float, metavar='FREQ', help="Upper frequency limit for analysis in Hz (accepts scientific notation, e.g., 1e6 for 1MHz)")
    
    args = parser.parse_args()
    plot_from_file(args.filename)
    if(args.fft):
        plot_fft(args.filename, db_scale=args.db, find_peaks_n=args.findpeaks, max_freq=args.maxfreq)
    plt.show()