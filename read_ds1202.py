#!/usr/bin/env python3
import argparse
import numpy as np
import sys
from datetime import datetime
from ds1202 import connect_to_scope, ds_1202_read_full


def generate_unique_filename(prefix="ds1202_data"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.npz"


def main():
    parser = argparse.ArgumentParser(description='Wrapper script for ds_1202_read_full function')
    parser.add_argument('ip_address', help='IP address of the oscilloscope')
    parser.add_argument('--prefix', '-p', default='ds1202_data',
                        help='Prefix for output filename (default: ds1202_data)')
    parser.add_argument('--channel', '-c', type=int, choices=[1, 2],
                        help='Oscilloscope channel to read (1 or 2). If not specified, tries both channels.')

    args = parser.parse_args()

    try:
        print(f"Connecting to oscilloscope at {args.ip_address}...")
        rm, scope = connect_to_scope(args.ip_address)

        channels_data = {}
        tdata = None

        if args.channel is not None:
            # Read specific channel
            print(f"Reading data from channel {args.channel}...")
            tdata, scope_data = ds_1202_read_full(scope, args.channel)
            channels_data[f'channel_{args.channel}'] = scope_data
        else:
            # Try both channels
            for channel in [1, 2]:
                try:
                    print(f"Attempting to read data from channel {channel}...")
                    tdata_ch, scope_data_ch = ds_1202_read_full(scope, channel)
                    channels_data[f'channel_{channel}'] = scope_data_ch
                    if tdata is None:
                        tdata = tdata_ch
                    print(f"Successfully read {len(scope_data_ch)} samples from channel {channel}")
                except RuntimeError as e:
                    print(f"Channel {channel}: {e}")
                    continue

            if not channels_data:
                print("Error: No channels could be read. Make sure at least one channel is enabled.", file=sys.stderr)
                sys.exit(1)

        filename = generate_unique_filename(args.prefix)
        print(f"Saving data to {filename}...")

        # Prepare data dictionary for saving
        save_data = {
            'time': tdata,
            'ip_address': args.ip_address,
            'channels_read': list(channels_data.keys())
        }
        save_data.update(channels_data)

        np.savez(filename, **save_data)

        print(f"Data saved successfully!")
        print(f"  Filename: {filename}")
        print(f"  Time samples: {len(tdata)}")
        print(f"  Channels saved: {', '.join(channels_data.keys())}")

        scope.close()
        rm.close()

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()