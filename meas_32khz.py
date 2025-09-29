#!/usr/bin/env python3
"""
Basic PyVISA script for DS1202 oscilloscope control
"""

import pyvisa
import time
from ds1202 import connect_to_scope, ds_1202_read_full
import numpy as np

#Initial Setup
def init_scope_settings(scope):
	
	# Set the offset to zero
	scope.write(':TIMebase:MAIN:OFFSet 0e-6')
	# Read timebase delay offset
	print("Reading timebase delay offset...")
	offset = scope.query(':TIMebase:MAIN:OFFSet?')
	print(f"Timebase delay offset: {offset.strip()}")

	#Enable Both Channels
	scope.write(":CHANnel1:DISPlay ON")
	stat = scope.query(":CHANnel1:DISPlay?")
	print(f"Channel 1 status: {stat.strip()}")
	scope.write(":CHANnel2:DISPlay ON")
	stat = scope.query(":CHANnel1:DISPlay?")
	print(f"Channel 2 status: {stat.strip()}")

	#set the mode
	scope.write(":TIMebase:MODE MAIN")

	#set timescale
	scope.write(":TIMebase:MAIN:SCALe 20e-6")
	tb = scope.query(":TIMebase:MAIN:SCALe?")
	tb_f = float(tb.strip())
	print(f"time/div = {tb_f}")

	scope.write(":CHANnel1:OFFSet 0") #
	scope.write(":CHANnel2:OFFSet 0")

	#important settings for read. will want to reference this for writing the full read data command
	"""
	For full raw data:
		1. You want the format to be ASCII - this is important because otherwise it's just a single byte, so conversion and resolution are lost
		2. You want the mode to be RAW, and you need to error out if you aren't in RAW or the scope is not stopped. Check for stop state before read, and enforce elsewhere
		3. We want the source to be both channels if they're both enabled, or one channel if only one is enabled. check for enable status to decide.
		4. Maximum size of one read is 15625 for ASCii. In order to read the full buffer you need to read multiple chunks in succession.
			4.1 in order to determine the memory depth, you must query the oscilloscope with :ACQuire:MDEPTH?. This sets the number of chunks
		5. timescale, etc might need to be reconstructed from ACQuire commands (i.e. sample rate)
	"""
	scope.write(":WAVeform:SOURce CHANnel2")

	rply = scope.query(":WAVeform:SOURce?")
	print(f"Source = {rply.strip()}")	
	rply = scope.query(":WAVeform:FORMat?")
	print(f"Format = {rply.strip()}")	
	rply = scope.query(":WAVeform:MODE?")
	print(f"MODE = {rply.strip()}")	

def main():
	try:
		rm, scope = connect_to_scope("10.0.4.104")
		init_scope_settings(scope)

		scope.write(":SINGle")

		# Optional: Query to verify command was received
		# (some scopes support :SINGle? to check trigger state)
		time.sleep(0.1)  # Small delay

		print("Command sent successfully!")

		triggered = 0
		st = time.time()
		while(time.time() - st < 10):	#10 second timeout
			stat = scope.query(":TRIGger:STATus?")
			print(stat.strip())
			if(stat.strip() == "STOP"):
				triggered = 1
				break
			time.sleep(1)	#only try 10 times to not spam the scope too much. should get it on the first
		if(triggered):
			td,ch2data = ds_1202_read_full(scope, 2)
			np.savez('data', td, ch2data)

			print("Data Acquired")
		else:
			print("Timed Out")

		# Close connection
		scope.close()
		rm.close()

	except pyvisa.VisaIOError as e:
		print(f"VISA Error: {e}")
	except Exception as e:
		print(f"Error: {e}")

if __name__ == "__main__":
	main()