import pyvisa
import time
import numpy as np


#TODO: build a ds1202 class

def connect_to_scope(ip):
	# Create resource manager
	rm = pyvisa.ResourceManager()

	# Connect to oscilloscope
	resource_string = f'TCPIP::{ip}::INSTR'
	print(f"Connecting to {resource_string}...")

	scope = rm.open_resource(resource_string)
	scope.timeout = 5000

	# Test connection with identification query
	print("Testing connection...")
	idn = scope.query('*IDN?')
	print(f"Connected to: {idn.strip()}")
	return rm, scope

"""
Returns, in volts, the data recovered from the full depth of available memory on the oscilloscope as a numpy array.
The length of the array corresponds to the mem depth with current settings.
Different settings (channels enabled, etc) may result in different sizes.
"""
def ds_1202_read_full_ascii(scope, chan):
	if(chan < 1 or chan > 2):
		raise RuntimeError("Source request channel out of range")
	
	#check status - ensure it is stopped
	stat = scope.query(":TRIGger:STATus?")
	if(stat.strip() != "STOP"):
		raise RuntimeError("Scope must be stopped before reading data")

	#Set desired source channel and verify it is selected properly
	scope.write(":WAVeform:SOURce CHANnel"+str(chan))
	rply = scope.query(":WAVeform:SOURce?")
	if(rply.strip() != "CHAN"+str(chan)):
		raise RuntimeError(f"Source request failed with response {rply.strip()}. Turn channel {chan} on!")

	#Set waveform formatting (ascii + raw)
	scope.write(":WAVeform:FORMat ASC")	#force ASC
	scope.write(":WAVeform:MODE RAW")

	rply = scope.query(":ACQuire:SRATe?")	
	sample_rate = float(rply.strip())
	# print(f"Sample Rate is {sample_rate} Sa/s")
	rply = scope.query(":TIMebase:MAIN:SCALe?")	
	timebase = float(rply.strip())
	# print(f"Timebase scale is set to {timebase} seconds")
	num_scales = 12	#not queryable
	max_readsize = 15625
	mem_depth = sample_rate*timebase*num_scales
	num_fullblocks = int(mem_depth/max_readsize)
	last_block_size = int(mem_depth) % int(max_readsize)
	blocksizes = [max_readsize]*num_fullblocks
	if(last_block_size != 0):
		blocksizes.append(last_block_size)
	
	# print(f"Must read {len(blocksizes)} blocks")
	# print(f"Block sizes: {blocksizes}")
	# print(f"Estimated memdepth: {mem_depth}")
	# print(f"Divisions: {num_fullblocks} full chunks with last chunk size {last_block_size}")

	rply = scope.query(":WAVeform:XINCrement?")
	xincrement = float(rply.strip())
	# print(f"x increment = {xincrement}")


	TMC_header_length = 11	#characters. for parsing

	scope_data_list = []
	start_pos = 1
	for i, blksize in enumerate(blocksizes):
		print(f"read number: {i+1} of {len(blocksizes)}")
		start = start_pos
		stop = start_pos + blksize - 1
		print("start: "+str(start)+" stop: " + str(stop))
		start_pos += blksize

		scope.write(":WAVeform:STARt "+str(start))			#TODO: multiple blocks based on mem depth
		scope.write(":WAVeform:STOP "+str(stop))

		data = scope.query(":WAVeform:DATA?").strip()
		TMC_header = data[0:TMC_header_length]
		data = data[TMC_header_length:]
		# print(f"Header = {TMC_header}")
		TMC_len = int(TMC_header[2:])
		if(len(data) != TMC_len):
			raise RuntimeError(f"Reported packet size mismatches recieved size")
		#TODO use xincrement to save time data
		data_parsed = np.fromstring(data, sep=',', dtype=float)
		scope_data_list.extend(data_parsed)

	scope_data = np.array(scope_data_list)
	if(len(scope_data) != int(mem_depth)):
		raise RuntimeError("Number of recovered samples does not match memory depth")
	tdata = np.linspace(0,timebase*num_scales, int(mem_depth))	#TODO: replace with mem_depth samples that increment by xincrement. More precise
	# if(tdata[1] - tdata[0] != xincrement):
	# 	raise RuntimeWarning(f"You may have fucked up your math: {xincrement} != {tdata[1] - tdata[0]}")
	return tdata, scope_data	#returns 1d numpy array of the data!


"""
Returns, in volts, the data recovered from the full depth of available memory on the oscilloscope as a numpy array,
as well as the time in seconds.

Faster than read_full_ascii. The scope has only 8 bit resolution ADC... jaezuts

The length of the array corresponds to the mem depth with current settings.
Different settings (channels enabled, etc) may result in different sizes.
"""
def ds_1202_read_full(scope, chan):
	if(chan < 1 or chan > 2):
		raise RuntimeError("Source request channel out of range")
	
	#check status - ensure it is stopped
	stat = scope.query(":TRIGger:STATus?")
	if(stat.strip() != "STOP"):
		raise RuntimeError("Scope must be stopped before reading data")

	#Set desired source channel and verify it is selected properly
	scope.write(":WAVeform:SOURce CHANnel"+str(chan))
	rply = scope.query(":WAVeform:SOURce?")
	if(rply.strip() != "CHAN"+str(chan)):
		raise RuntimeError(f"Source request failed with response {rply.strip()}. Turn channel {chan} on!")

	#Set waveform formatting (ascii + raw)
	scope.write(":WAVeform:FORMat BYTE")	#force ASC
	scope.write(":WAVeform:MODE RAW")

	rply = scope.query(":ACQuire:SRATe?")	
	sample_rate = float(rply.strip())
	# print(f"Sample Rate is {sample_rate} Sa/s")
	rply = scope.query(":TIMebase:MAIN:SCALe?")	
	timebase = float(rply.strip())
	# print(f"Timebase scale is set to {timebase} seconds")
	num_scales = 12	#not queryable
	max_readsize = 250000
	mem_depth = sample_rate*timebase*num_scales
	num_fullblocks = int(mem_depth/max_readsize)
	last_block_size = int(mem_depth) % int(max_readsize)
	blocksizes = [max_readsize]*num_fullblocks
	if(last_block_size != 0):
		blocksizes.append(last_block_size)
	# print(f"Must read {len(blocksizes)} blocks")
	# print(f"Block sizes: {blocksizes}")
	# print(f"Estimated memdepth: {mem_depth}")
	# print(f"Divisions: {num_fullblocks} full chunks with last chunk size {last_block_size}")

	rply = scope.query(":WAVeform:XINCrement?")
	xincrement = float(rply.strip())
	rply = scope.query("WAVeform:YINCrement?")
	yincrement = float(rply.strip())
	rply = scope.query(":WAVeform:YORigin?")
	yorigin = float(rply.strip())
	rply = scope.query(":WAVeform:YREFerence?")
	yreference = float(rply.strip())
	print(f"Yorigin = {yorigin}, Yincrement = {yincrement}, Yreference = {yreference}")
	# print(f"x increment = {xincrement}")


	TMC_header_length = 11	#characters. for parsing
	
	scope_data_list = []
	start_pos = 1
	for i, blksize in enumerate(blocksizes):
		print(f"read number: {i+1} of {len(blocksizes)}")
		start = start_pos
		stop = start_pos + blksize - 1
		print("start: "+str(start)+" stop: " + str(stop))
		start_pos += blksize

		scope.write(":WAVeform:STARt "+str(start))			#TODO: multiple blocks based on mem depth
		scope.write(":WAVeform:STOP "+str(stop))

		scope.write(":WAVeform:DATA?")
		data = scope.read_raw()
		TMC_header = data[0:TMC_header_length].decode('ascii')
		data = data[TMC_header_length:]
		print(f"Header = {TMC_header}")
		TMC_len = int(TMC_header[2:])
		data = data[0:TMC_len]
		if(len(data) != TMC_len):
			raise RuntimeError(f"Reported packet size {TMC_len} mismatches recieved size {len(data)}")
		#TODO use xincrement to save time data
		# data_parsed = np.fromstring(data, sep=',', dtype=float)
		
		data_parsed = np.frombuffer(data, dtype=np.uint8)
		data_float = (data_parsed.astype(float) - yorigin - yreference)*yincrement
		scope_data_list.extend(data_float)

	scope_data = np.array(scope_data_list)
	if(len(scope_data) != int(mem_depth)):
		raise RuntimeError("Number of recovered samples does not match memory depth")
	tdata = np.linspace(0,timebase*num_scales, int(mem_depth))	#TODO: replace with mem_depth samples that increment by xincrement. More precise
	# if(tdata[1] - tdata[0] != xincrement):
	# 	raise RuntimeWarning(f"You may have fucked up your math: {xincrement} != {tdata[1] - tdata[0]}")
	return tdata, scope_data	#returns 1d numpy array of the data!


