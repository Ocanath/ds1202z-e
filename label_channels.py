import numpy as np
import sys
import argparse
from pathlib import Path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Add labels to channel data in .npz files')
    parser.add_argument('filename', help='.npz file to add labels to')
    parser.add_argument('-d', '--description', action='store_true', help='Add description field')

    args = parser.parse_args()

    filename = Path(args.filename)

    if not filename.exists():
        print(f"Error: File {filename} not found")
        sys.exit(1)

    # Load the data
    data = np.load(filename)

    # Convert to a mutable dictionary
    data_dict = dict(data)

    # Find all channel_n keys
    channel_keys = [key for key in data_dict.keys() if key.startswith('channel_')]

    if not channel_keys:
        print("No channel data found in file")
        sys.exit(1)

    print(f"Found channels: {', '.join(channel_keys)}")
    print()

    # Prompt for labels for each channel
    for channel_key in sorted(channel_keys):
        # Extract channel number
        channel_num = channel_key.split('_')[1]
        label_key = f'ch_{channel_num}_label'

        # Show existing label if present
        if label_key in data_dict:
            print(f"Current label for {channel_key}: {data_dict[label_key]}")

        # Prompt for new label
        label = input(f"Channel {channel_num} Label: ")
        data_dict[label_key] = label

    # Prompt for description if flag is set
    if args.description:
        print()
        if 'description' in data_dict:
            print(f"Current description: {data_dict['description']}")

        description = input("Description: ")
        data_dict['description'] = description

    # Save back to file
    np.savez(filename, **data_dict)
    print(f"\nLabels saved to {filename}")