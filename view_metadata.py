import numpy as np
import sys
from pathlib import Path
from pprint import pprint


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python view_metadata.py <filename.npz>")
        sys.exit(1)

    filename = Path(sys.argv[1])

    if not filename.exists():
        print(f"Error: File {filename} not found")
        sys.exit(1)

    # Load the data
    data = np.load(filename)

    # Filter out channel_n data entries
    metadata = {key: data[key] for key in data.keys() if not (key.startswith('channel_') or key.startswith('time'))}

    if not metadata:
        print("No metadata found in file")
    else:
        print(f"Metadata for {filename.name}:")
        print()
        pprint(metadata)