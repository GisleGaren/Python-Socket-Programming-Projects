import socket
import sys
import time
import argparse
import threading

# Description:
# This function is responsible for slicing up the total interval time defined by -t into -i time chunks and will print out each the data transfers one
# by one with each row being defined by the -i interval flag. At the end of the total time interval given by -t, it will also display the total transfer
# and the total time elapsed.
# Arguments:
# client_socket: this is the client socket object that is created from the parallel_send_data function which defines a specific connection to the server. It utilizes the TCP transport protocol and IPv4 address family.
# server_ip: this holds the ip address of the server using the IPv4 address family. If not specified by the -b flag, the default server_ip is 127.0.0.1 which is the ip of the local machine itself.
# port: port number of the server between 1024 and 65535. If not specified by the -p flag, the default port is 8088.
# start_time: is time.time() which shows time elapsed after January 1, 1970, 00:00:00, in this case we start the timer from when the function is called.
# duration: is the amount of time in seconds defined by the -t flag which defines how long we want the connection to send information in bytes. If not specified, default duration is 25 seconds.
# interval: defines how long each interval being printed should last given a duration -t in seconds. 
# unit: is the format that we define by the -f flag, it has to either be 'B', 'KB' or 'MB'.
# Returns: 
# A variable called total_data_sent because we are interested in printing out in the last row the total amount of data transferred and we want to know the bandwidth of that transfer.

def print_interval_stats(client_socket, server_ip, port, start_time, duration, interval, unit):
	total_data_sent = 0						# Initialize the total_data_sent variable to track how much data is transferred
	interval_data_sent = 0  				# Initialize the interval_data_sent variable to track how much data is transferred in each interval
	interval_start_time = start_time 		# Interval start time same as the function parameter start_time
	data_chunk = b'\0' * 1000				# Making sure that each time we use the .send() function, we send information in the form of 1000 bytes each time

	while time.time() - start_time < duration: 			# The difference between the start_time and the time elapsed cannot be more than the duration
		sent = client_socket.send(data_chunk)			# define variable sent which sends data chunks in 1000 bytes to the server
		total_data_sent += sent							# Update total data sent 
		interval_data_sent += sent  					# Update the interval data sent

		current_time = time.time() 										# Time at that very second
		elapsed_interval_time = current_time - interval_start_time  	# Check that the time elapsed has not gone more than the interval time -i

		# Check to see if the interval time elapsed is  >= to the defined interval, then we print. Second condition to make sure the last statistic is printed
		if elapsed_interval_time >= interval or time.time() - start_time >= duration: 			
			interval_end_time = current_time 									# Replace the current_time with the end time
			sent_data = (interval_data_sent / format_to_bytes(1, unit)) 		# Convert the sent_data to its respective unit of measurement
			bandWidth_MB = (interval_data_sent / format_to_bytes(1,"MB") * 8)   # Bandwidth should be displayed in Mbps
			interval_bandwidth = bandWidth_MB / elapsed_interval_time 			# Divide the newly converted Mbps by the elapsed interval time
			
			# Format each print via 4 columns with 20 spaces each column. Content in the .format() is split up by the comma
			print("{:<20}{:<20}{:<20}{:<20}".format(f"{server_ip}:{port}", f"{interval_start_time - start_time:.1f} - {interval_end_time - start_time:.1f}", f"{int(sent_data)} {unit}", f"{interval_bandwidth:.2f} Mbps"))
			interval_start_time = interval_end_time								# Start interval time is now from where we left off at the last one
			interval_data_sent = 0  											# Reset the interval data sent and the line shift below is for formatting the terminal output
	print("\n----------------------------------------------------------------------------------- \n")			 
	return total_data_sent						# Return total data sent for use in the summary statistic

# Description:
# This function is responsible for making sure that the total amount of data being sent from the client to the server does not exceed the defined limit.
# The number of bytes transferred should be in either B, KB or MB.
# Arguments:
# client_socket: This is the client socket object that is created from the parallel_send_data function which defines a specific connection to the server. It utilizes the TCP transport protocol and IPv4 address family.
# numbytes: Amount of bytes to transfer specified by the -n flag.
# Returns: 
# A variable called total_data_sent because we are interested in printing out in the last row the total amount of data transferred and we want to know the bandwidth of that transfer.

def send_data_with_numbytes(client_socket, numbytes):
	total_data_sent = 0								# Initialize the total_data_sent variable to track how much data is transferred
	data_chunk = b'\0' * 1000						# Making sure that each time we use the .send() function, we send information in the form of 1000 bytes each time

	while total_data_sent < numbytes:				# As long as the total amount of data we have sent does not exceed the -n limit, keep sending
		sent = client_socket.send(data_chunk)		# define variable sent which sends data chunks in 1000 bytes to the server
		total_data_sent += sent						# Update total data sent 

	return total_data_sent							# Return total data sent for use in the summary statistic



# Description:
# This function is responsible for handling each thread which is initiated from the run_server() function. It takes in a connection object which actually
# is the socket that is created in "connection, address = server_socket.accept()" where the socket represents a specific connection between the client and
# the server. The function takes in a connection socket and handles that client connection where it will keep on receiving chunks of 1000 bytes from the
# client until it receives a BYE string from the client, close the connection, prepare the variables for the output and then print them out.
# Arguments:
# connection: this is the socket that is created in the run_server which represents a specific connection between server and client.
# address: array containining two parameters which are the ip address and the port number of the client that is connected to the server.
# unit: is the format that we define by the -f flag, it has to either be 'B', 'KB' or 'MB'.
# Returns: 
# Void. The function doesn't return anything.

def handle_connection(connection, address, unit):
	start_time = time.time()					# Define start time
	total_data_received = 0						# Initialize the total_data_received variable to track how much data has been received

	try:										
		while True:
			data = connection.recv(1000)		# define variable data which receives data chunks in 1000 bytes in the server
			total_data_received += len(data)    # We must have len() because data is a bytes object and len() returns the length of the object i.e byte size

			if data == b'BYE':					
				connection.send(b'ACK')			# If we receive a 'BYE' String from the client, return an 'ACK' String and break out
				break

			if not data:						# If we don't receive data we also need to break out of the while loop
				break

	except Exception as e:						# Throw an Exception if the server can't handle the connection
		print(f"An error occurred while handling the connection: {e}")

	connection.close()							# Close connection as soon as we don't need it anymore

	elapsed_time = time.time() - start_time									# Measure time elapsed
	received_data = total_data_received / format_to_bytes(1, unit)			# Convert the received data into the specified format
	bandWidth_Mbps = (total_data_received / format_to_bytes(1, "MB") * 8)	# Convert bandwidth from megabytes to megabits
	bandwidth = bandWidth_Mbps / elapsed_time								# Get the average bandwidth

	# Print header and summary statistic for each connection
	print("{:<20}{:<20}{:<20}{:<20}".format("ID", "Interval", "Transfer", "Bandwidth"))
	print("{:<20}{:<20}{:<20}{:<20}".format(f"{address[0]}:{address[1]}", f"0.0 - {elapsed_time:.2f}", f"{int(received_data)} {unit}", f"{bandwidth:.2f} Mbps"))


# Description:
# This function is responsible for running the server and starts off by defining a server socket which is specified by the -b bind flag which selects
# the ip address of the server's interface where the client connects. Once the server socket has bound itself to the ip address and port, it will listen
# for incoming connections with a limit of 5 connections at once. The server will then keep on refreshing to accept new connections generating a connection
# socket object as well as an address array, which the server function will pass on as arguments to the thread object connection_thread. "target" specifies the function that
# the thread should run and passes along relevant arguments. Once the thread object is created, we run it using the .start() method which runs the function in a separate thread
# allowing the server to handle multiple clients simultaneously. This keeps going as long as there are more clients that want to connect.
# Arguments:
# ip: the IP address of the server's interface using the IPv4 address family. If not specified by the -b flag, the default server_ip is 127.0.0.1 which is the ip of the local machine itself.
# port: port number of the server between 1024 and 65535. If not specified by the -p flag, the default port is 8088.
# unit: is the format that we define by the -f flag, it has to either be 'B', 'KB' or 'MB'.
# Returns: 
# Void. The function doesn't return anything.

def run_server(ip, port, unit):
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)			# Create a server socket utiziling IPv4 and TCP
	server_socket.bind((ip, port))												# Bind the server socket interface to the specified ip and port from the terminal
	server_socket.listen(5)														# Server listens to up to 5 connections

	# Print that the server is listening on the given ip and port from the terminal
	print("----------------------------------------------------")
	print(f"A simpleperf server is listening on {ip}:{port}")
	print("----------------------------------------------------")
	
	# Loop that keeps on going and accepts new connections creating a connection socket representing a connection between the client and the server and creates a tuple
	# containing the ip address and port number of the client that has connected to the server. All this is done via .accept() We then print out 
	while True:
		connection, address = server_socket.accept()													# Create a connection socket representing the connection between client and server and create tuple with client ip and port
		print(f"A simpleperf client with {address} is connected with server ('{ip}', {port}) \n")		# Print the info of the specific client that has connected

		# Create a new thread to handle this connection
		connection_thread = threading.Thread(target=handle_connection, args=(connection, address, unit))	# Create a thread object that will run the handle_connection() function when started
		connection_thread.start()																			# Start the thread object that was recently instantiated


"""
Description:
This function is responsible for sending data to the server in parallel connections, either using the number of bytes or the time interval.
It also prints out statistics about the transfer at specified intervals if an interval is defined.
Arguments:
server_ip: holds the ip address of the server using the IPv4 address family. If not specified by the -b flag, the default server_ip is 127.0.0.1 which is the ip of the local machine itself.
port: port number of the server between 1024 and 65535. If not specified by the -p flag, the default port is 8088.
duration: is the amount of time in seconds defined by the -t flag which defines how long we want the connection to send information in bytes. If not specified, default duration is 25 seconds.
unit: is the format that we define by the -f flag, it has to either be 'B', 'KB' or 'MB'.
interval: defines how long each interval being printed should last given a duration -t in seconds.
numbytes: defines the total number of bytes that will be sent to the server.
connection: indicates the id of the parallel connection.
connection_thread: this variable holds the handle for the parallel connection.
start_time: is time.time() which shows time elapsed after January 1, 1970, 00:00:00, in this case we start the timer from when the function is called.
client_socket: this is the client socket object that is created from the parallel_send_data function which defines a specific connection to the server. It utilizes the TCP transport protocol and IPv4 address family.
Returns:
None. """


def parallel_send_data(server_ip, port, duration, unit, interval, numbytes, connection):
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	client_socket.connect((server_ip, port))
	client_ip = client_socket.getsockname()[0]
	client_port = client_socket.getsockname()[1]
	print(f"Client {client_ip}:{client_port} connected with server {server_ip} {port}")

	time.sleep(0.01) # Need this to make sure that all the parallel connections get the time to print the message above before the header
	if connection == 1:
		print() # Space between the last connection printed and the transfer headers
		print("{:<20}{:<20}{:<20}{:<20}".format("ID", "Interval", "Transfer", "Bandwidth"))
	
	start_time = time.time()	
	if numbytes:
		total_data_sent = send_data_with_numbytes(client_socket, numbytes)
	elif interval:
		total_data_sent = print_interval_stats(client_socket, server_ip, port, time.time(), duration, interval, unit)
	else:
		total_data_sent = 0
		data_chunk = b'\0' * 1000

		while time.time() - start_time < duration:
			sent = client_socket.send(data_chunk)
			total_data_sent += sent

	#print(f"{connection} has transferred {total_data_sent} bytes") # For å sjekke hvor mange bytes hver connection sender
	client_socket.send(b'BYE')
	ack = client_socket.recv(1024)

	if ack == b'ACK':
		# print("Vi fikk tilbake en ACK")
		elapsed_time = time.time() - start_time
		if elapsed_time < 1:
			elapsed_time = 1
		sent_data = total_data_sent / format_to_bytes(1, unit)
		bandwidth_MB = (total_data_sent / format_to_bytes(1, "MB") * 8)
		bandwidth = bandwidth_MB / elapsed_time
		
		print("{:<20}{:<20}{:<20}{:<20}".format(f"{server_ip}:{port}", f"0.0 - {elapsed_time:.2f}", f"{int(sent_data)} {unit}", f"{bandwidth:.2f} Mbps"))

	client_socket.close()

def run_client(server_ip, port, duration, unit, interval, parallel, numbytes):
	print("---------------------------------------------")
	print(f"A simpleperf client connecting to server {server_ip}, port {port}")
	print("---------------------------------------------")
	print()

	threads = []

	# Create a thread object using the Thread() constructor from the "threading" module 
	for i in range(parallel): # target parameter states which function should be called when thread starts running
		t = threading.Thread(target=parallel_send_data, args=(server_ip, port, duration, unit, interval, numbytes, i + 1))
		t.start() # Start the thread after defining it
		threads.append(t) # Add it to the array list

	for t in threads: # WAit for all the threads to finish executing before proceeding with the rest of the program
		t.join() # the join() method ensures that all the threads have been executed before we move onto the next line of the run_client() code. Exception handling t.join(interval +2)
		# In this case it is nothing, because there is no more code in the run_client() method after line 188.

# Function to parse command line arguments
def parse_arguments():
	parser = argparse.ArgumentParser(description="A simple network throughput measurement tool")
	parser.add_argument("-s", "--server", action="store_true", help="Run in server mode")
	parser.add_argument("-c", "--client", action="store_true", help="Run in client mode")
	parser.add_argument("-b", "--bind", type=str, default="127.0.0.1", help="Select the IP address of the server's interface (default: 127.0.0.1)")
	parser.add_argument("-I", "--ip", type=str, default="127.0.0.1", help="Server IP address (default: 127.0.0.1)")
	parser.add_argument("-p", "--port", type=int, default=8088, help="Port number (default: 8088)")
	parser.add_argument("-t", "--time", type=int, default=25, help="Duration in seconds (default: 25)")
	parser.add_argument("-f", "--format", type=str, choices=["B", "KB", "MB"], default="MB", help="Format in B, KB or MB (default: MB)")
	parser.add_argument("-i", "--interval", type=int, help="Print statistics per interval in seconds")
	parser.add_argument("-P", "--parallel", type=int, default=1, help="Number of parallel connections (default: 1)")
	parser.add_argument("-n", "--numbytes", type=str, help="Number of bytes to transfer (For example: 100B, 1KB, 10MB)")

	args = parser.parse_args()

	if args.port not in range(1024, 65536):
		print("Error: port number must be in the range between 1024 and 65535")
		sys.exit(1)

	if args.time <= 0:
		print("Error: -t flag must be greater than 0")
		sys.exit(1)

	if args.interval is not None and args.interval <= 0:  		# Need "is not None" because we don't have a default -i value
		print("Error: interval must be a positive integer")
		sys.exit(1)

	if args.parallel not in range(1,6):
		print("Error: the number of parallel connections can only be between 1 to 5")
		sys.exit(1)

	if args.numbytes: # If we provide the "-n" command in the terminal, then we go into the if statement. For example "-n 10MB"
		num_bytes_value = int(args.numbytes[:-2]) # This converts the number values of the numbytes command string into an int. The [:-2] slices the string to remove the last two letters in this case "MB" so that "10" is converted to an int.
		if args.numbytes[-2:] != "MB" and args.numbytes[-2:] != "KB": # Incase we type "15B" then "args.numbytes[-2:]" would return "5B" which will return an error in the "format_to_bytes" function
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
	elif args.server:
		run_server(args.bind,args.port,args.format) # Default server settings would be data transfer in MegaBytes and port number 8088.
	else:
		print("Error, you must select server or client mode")
		sys.exit(1)