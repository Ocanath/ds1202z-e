#!/usr/bin/env python3
"""
Basic PyVISA script for DS1202 oscilloscope control
"""

import pyvisa
import time
from ds1202 import connect_to_scope


def main():
	try:
		rm, scope = connect_to_scope("10.0.1.104")

		# Send single trigger command
		print("Sending :SINGle command...")
		scope.write(':SINGle')

		# Optional: Query to verify command was received
		# (some scopes support :SINGle? to check trigger state)
		time.sleep(0.1)  # Small delay

		print("Command sent successfully!")

		# Close connection
		scope.close()
		rm.close()

	except pyvisa.VisaIOError as e:
		print(f"VISA Error: {e}")
	except Exception as e:
		print(f"Error: {e}")

if __name__ == "__main__":
	main()