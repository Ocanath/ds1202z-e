# Rigol DS1000z Series Oscilloscope Read Library

## Introduction

This codebase uses numpy and pyvisa to implement some general purpose TCP data offloading and oscilloscope configuration tools for the DS1000 series oscilloscopes. It is essentially just a set of convenient wrapper functions for SCPI commands with error correction, checking and handling, and configuration to obtain full depth oscilloscope data from memory for offline analysis.

## Installation

### Prerequisites
- Python 3.6 or higher
- VISA drivers (NI-VISA or equivalent) for instrument communication

For optional post-analysis software:
- matplotlib
- scipy


### Install Dependencies
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install pyvisa numpy matplotlib scipy
```

## Usage

### Data Acquisition with read_ds1202.py

Wrapper script for capturing oscilloscope data with automatic channel detection and file saving.

```bash
# Capture data from all available channels
python read_ds1202.py 192.168.1.100

# Capture data from specific channel with custom filename prefix
python read_ds1202.py 192.168.1.100 --channel 1 --prefix my_measurement

# Try both channels with custom prefix
python read_ds1202.py 192.168.1.100 --prefix experiment_1
```

**Arguments:**
- `ip_address` (required): IP address of the oscilloscope
- `--channel`, `-c`: Specific channel to read (1 or 2). If not specified, tries both channels
- `--prefix`, `-p`: Filename prefix for saved data (default: "ds1202_data")

**Output:**
- Saves data as `.npz` files with unique timestamps
- Contains time data, voltage data for each channel, and metadata

### Data Visualization with plot_utils.py

Plot time-domain and frequency-domain data from saved `.npz` files.

```bash
# Plot time-domain data only
python plot_utils.py data_file.npz

# Plot both time-domain and FFT magnitude spectrum
python plot_utils.py data_file.npz --fft

# Plot FFT in dB scale with peak detection
python plot_utils.py data_file.npz --fft --db --findpeaks 5
```

**Arguments:**
- `filename` (required): Path to the `.npz` data file
- `--fft`: Generate FFT magnitude spectrum plot (overlaid for multiple channels)
- `--db`: Plot FFT magnitude in dB scale (only with `--fft`)
- `--findpeaks N`: Find and display N largest peaks per channel (only with `--fft`)

**Features:**
- Automatically detects and plots all available channels
- Time-domain: Overlaid channel plots
- Frequency-domain: FFT magnitude spectrum in kHz with overlaid channels
- Peak analysis: Identifies and marks dominant frequency components
- Dual scaling: Linear voltage or logarithmic dB display