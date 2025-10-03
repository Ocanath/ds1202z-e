import argparse
import sys
from ds1202 import connect_to_scope
import time

def main():
    parser = argparse.ArgumentParser(description='Wrapper script for ds_1202_read_full function')
    parser.add_argument('ip_address', help='IP address of the oscilloscope')

    args = parser.parse_args()

    try:
        print(f"Connecting to oscilloscope at {args.ip_address}...")
        rm, scope = connect_to_scope(args.ip_address)
        print("Single trigger now...")
        scope.write(":SINGle")
        time.sleep(0.001)
        print("Waiting for trigger to stop (no timeout!)")
        while(1):
            stat = scope.query(":TRIGger:STATus?")
            if(stat.strip() == "STOP"):
                break
            time.sleep(0.1)
            #if(stat.strip() != "STOP"):
                #raise RuntimeError("Scope must be stopped before reading data")
        print("Stopped.")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()