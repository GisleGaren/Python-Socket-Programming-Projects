import socket
import sys
import time
import argparse

# To do list from 24.03.23. Check the bandwidth, is the information we are getting and sending back and forth of the right format? B, KB or MB?
# Go through the code line for line and learn what it does.

def print_interval_stats(client_socket, server_ip, port, start_time, duration, interval, unit):
	total_data_sent = 0
	interval_data_sent = 0  # New variable to store data sent during the current interval   
	interval_start_time = start_time  # Start time of the interval = start_time parameter which is the timer from when the connection is established
	data_chunk = b'\0' * 1000

	while time.time() - start_time < duration: # The difference between the start_time and the time elapsed cannot be more than the duration
		sent = client_socket.send(data_chunk)
		total_data_sent += sent
		interval_data_sent += sent  # Update the interval data sent

		current_time = time.time() # Time at that very second
		elapsed_interval_time = current_time - interval_start_time  # we need this to check that the time elapsed has not gone more than the
		# interval time -i. .send() function will happen many times per second so elapsed_interval_time variable updates VERY frequently!

		# Without the "or time.time() - start_time >= duration" part of the if statement, the last interval would not get printed out
		# In the case of "python3 simpleperf.py -c -t 10 -i 2" the reason the last interval wasn't printed out is that 
		if elapsed_interval_time >= interval or time.time() - start_time >= duration: # If the interval time is greater than or equal to the interval, then we print
			interval_end_time = current_time # Replace the current_time with the end time
			sent_data = (interval_data_sent / format_to_bytes(1, unit)) # Convert the sent_data to its respective unit of measurement
			bandWidth_MB = (interval_data_sent / format_to_bytes(1,"MB") * 8)
			interval_bandwidth = bandWidth_MB / elapsed_interval_time # How much data was sent in that interval?
			
			print("{:<20}{:<20}{:<20}{:<20}".format(f"{server_ip}:{port}", f"{interval_start_time - start_time:.1f} - {interval_end_time - start_time:.1f}", f"{int(sent_data)} {unit}", f"{interval_bandwidth:.2f} Mbps"))
			# the print function above prints as the second column, the 
			interval_start_time = interval_end_time
			interval_data_sent = 0  # Reset the interval data sent

	return total_data_sent

def run_server(ip, port, unit):
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.bind((ip, port))
	server_socket.listen(1)

	print("---------------------------------------------")
	print(f"A simpleperf server is listening on {ip}:{port}")
	print("---------------------------------------------")

	while True:
		connection, address = server_socket.accept()
		print(f"A simpleperf client with {address} is connected with server ('{ip}', {port}) \n")

		start_time = time.time() # Marks the starting point of the timer which is when we have established the connection
		total_data_received = 0 # initilializa the total data received variable

		try:
			while True:
				data = connection.recv(1000) # The connection keeps receiving chunks of data in 1000 bytes
				total_data_received += len(data) # Adds the chunks of data and appends it 

				if data == b'FINISH': # The server keeps receiving data in 1000 byte chunks until the client sends a string "FINISH" to the server
					connection.send(b'ACK') # The server then sends an acknowledgement back to the client and breaks out of the while loop.
					break

				if not data:
					break
		finally: # Finally is thrown in whether an exception is raised or not, so that the connection closes even if an error occurs.
			connection.close()

		elapsed_time = time.time() - start_time
		received_data = total_data_received / format_to_bytes(1, unit)  # If for example we have KB, then we need to divide total_data_received by what format_to_bytes(1, "KB") returns which would be 1000.
		bandWidth_MB = (total_data_received / format_to_bytes(1,"MB") * 8) # We need this because the portfolio asks for us to always get the bandwidth in Mbps
		bandwidth = bandWidth_MB / elapsed_time 

		print("{:<20}{:<20}{:<20}{:<20}".format("ID", "Interval", "Received", "Rate"))
		print("{:<20}{:<20}{:<20}{:<20}".format(f"{address[0]}:{address[1]}", f"0.0 - {elapsed_time:.2f}", f"{int(received_data)} {unit}", f"{bandwidth:.2f} Mbps"))

	#	I believe I need to add connection.close() here as the task says that the server gracefully closes the connection when the above is printed.

def run_client(server_ip, port, duration, unit, interval, parallel, numbytes):
	# Create a TCP socket
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# Connect to the server
	client_socket.connect((server_ip, port))
	print("---------------------------------------------")
	print(f"A simpleperf client connecting to server {server_ip}, port {port}")
	print("---------------------------------------------")

	print("{:<20}{:<20}{:<20}{:<20}".format("ID", "Interval", "Transfer", "Bandwidth"))
	start_time = time.time() # Start the timer as soon as the connection has started

	if interval:
		total_data_sent = print_interval_stats(client_socket, server_ip, port, start_time, duration, interval, unit)
	else:
		total_data_sent = 0
		data_chunk = b'\0' * 1000

		while time.time() - start_time < duration:
			sent = client_socket.send(data_chunk)
			total_data_sent += sent

	# Send the finish/bye message
	client_socket.send(b'FINISH') # Once the duration time has elapsed, send the "FINISH" string to the server

	# Wait for the acknowledgement
	ack = client_socket.recv(1024) # The server should then send a String "ACK" to the client

	if ack == b'ACK':
		elapsed_time = time.time() - start_time
		sent_data = total_data_sent / format_to_bytes(1, unit)  # If for example we have KB, then we need to divide total_data_received by what format_to_bytes(1, "KB") returns which would be 1000.
		bandwidth_MB = (total_data_sent / format_to_bytes(1,"MB") * 8) # We need this because the portfolio asks for us to always get the bandwidth in Mbps
		bandwidth = bandwidth_MB / elapsed_time

		print("\n----------------------------------------------------------------------------------- \n")
		print("{:<20}{:<20}{:<20}{:<20}".format(f"{server_ip}:{port}", f"0.0 - {elapsed_time:.2f}", f"{int(sent_data)} {unit}", f"{bandwidth:.2f} Mbps"))

	client_socket.close()

# Function to parse command line arguments
def parse_arguments():
	parser = argparse.ArgumentParser(description="A simple network throughput measurement tool")
	parser.add_argument("-s", "--server", action="store_true", help="Run in server mode")
	parser.add_argument("-c", "--client", action="store_true", help="Run in client mode")
	parser.add_argument("-b", "--bind", type=str, default="0.0.0.0", help="Server IP address (default: 0.0.0.0)")
	parser.add_argument("-I", "--ip", type=str, default="127.0.0.1", help="Client IP address (default: 127.0.0.1)")
	parser.add_argument("-p", "--port", type=int, default=8088, choices=range(1024, 65536), help="Port number (default: 8088)")
	parser.add_argument("-t", "--time", type=int, default=25, help="Duration in seconds (default: 25)")
	parser.add_argument("-f", "--format", type=str, choices=["B", "KB", "MB"], default="MB", help="Summary format (default: MB)")
	parser.add_argument("-i", "--interval", type=int, help="Print statistics per interval seconds")
	parser.add_argument("-P", "--parallel", type=int, default=1, choices=range(1, 6), help="Number of parallel connections (default: 1)")
	parser.add_argument("-n", "--numbytes", type=str, help="Number of bytes to transfer (e.g., 100B, 1KB, 10MB)")

	args = parser.parse_args()

	if args.numbytes: # If we provide the "-n" command in the terminal, then we go into the if statement. For example "-n 10MB"
		num_bytes_value = int(args.numbytes[:-2]) # This converts the number values of the numbytes command string into an int. The [:-2] slices the string to remove the last two letters in this case "MB" so that "10" is converted to an int.
		if args.numbytes[-2:] != "MB" or args.numbytes[-2:] != "KB": # Incase we type "15B" then "args.numbytes[-2:]" would return "5B" which will return an error in the "format_to_bytes" function
			num_bytes_unit = args.numbytes[-1:] # If for example we type "15B" in the terminal, we would only take in the last letter "B" and pass it as an arguemtn into format_to_bytes
		else:
			num_bytes_unit = args.numbytes[-2:] # This returns the last two letters of a String so "10MB" turns into "MB"
		args.numbytes = format_to_bytes(num_bytes_value, num_bytes_unit) # After we have split the "10MB" into 10 and "MB" respectively, we add those as arguments into the format_to_bytes function.

	return args # We return an "args" object with a list of values ("client" = True, "server" = False, "ip" = 192.168.1.0, etc...)

def format_to_bytes(value, unit): # This function converts the units to their rightful value. For MB we have to divide by 1000000 to go from B to MB
	if unit == "B":
		return value
	elif unit == "KB":
		return value * 1000
	elif unit == "MB":
		return value * 1000 * 1000
	else:
		raise ValueError(f"Invalid unit: {unit}")

if __name__ == "__main__":
	args = parse_arguments() # Example of what the args object could have is: args = { "client": True, "server": False, "ip": "192.168.1.100", "port": 8888, "time": 30, "format": "MB", "interval": 5, "parallel": 2, "numbytes": 10000000 } 

	if args.server and args.client:
		print("Error: you must run either in server or client mode, not both")
		sys.exit(1)
	elif args.client:
		run_client(args.ip, args.port, args.time, args.format, args.interval, args.parallel, args.numbytes)
	else:
		run_server(args.bind,args.port, args.format) # Default server settings would be data transfer in MegaBytes and port number 8088.