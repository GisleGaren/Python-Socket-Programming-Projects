import socket
import sys
import time
import argparse
import threading
import re

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
# interval: defines how long each interval being printed in seconds.
# unit: is the format that we define by the -f flag, it has to either be 'B', 'KB' or 'MB'.
# Returns: 
# A variable called total_data_sent because we are interested in printing out in the last row the total amount of data transferred and we want to know the bandwidth of that transfer.

def print_interval_stats(client_socket, server_ip, port, start_time, duration, interval, unit):
	total_data_sent = 0												# Initialize the total_data_sent variable to track how much data is transferred
	interval_data_sent = 0  										# Initialize the interval_data_sent variable to track how much data is transferred in each interval
	interval_start_time = start_time 								# Interval start time same as the function parameter start_time
	data_chunk = b'\0' * 1000										# Making sure that each time we use the .send() function, we send information in the form of 1000 bytes each time

	while time.time() - start_time < duration: 						# The difference between the start_time and the time elapsed cannot be more than the duration
		sent = client_socket.send(data_chunk)						# define variable sent which sends data chunks in 1000 bytes to the server
		total_data_sent += sent										# Update total data sent 
		interval_data_sent += sent  								# Update the interval data sent

		current_time = time.time() 													# Time at that very second
		elapsed_interval_time = current_time - interval_start_time  				# Check that the time elapsed has not gone more than the interval time -i

		# Check to see if the interval time elapsed is  >= to the defined interval, then we print. Second condition to make sure the last statistic is printed
		if elapsed_interval_time >= interval or time.time() - start_time >= duration: 			
			interval_end_time = current_time 												# Replace the current_time with the end time
			sent_data = (interval_data_sent / format_to_bytes(1, unit)) 					# Convert the sent_data to its respective unit of measurement
			bandWidth_MB = (interval_data_sent / format_to_bytes(1,"MB") * 8)   			# Bandwidth should be displayed in Mbps
			interval_bandwidth = bandWidth_MB / elapsed_interval_time 						# Divide the newly converted Mbps by the elapsed interval time
			
			# Format each print via 4 columns with 20 spaces each column. Content in the .format() is split up by the comma
			print("{:<20}{:<20}{:<20}{:<20}".format(f"{server_ip}:{port}", f"{interval_start_time - start_time:.1f} - {interval_end_time - start_time:.1f}", f"{int(sent_data)} {unit}", f"{interval_bandwidth:.2f} Mbps"))
			interval_start_time = interval_end_time											# Start interval time is now from where we left off at the last one
			interval_data_sent = 0  														# Reset the interval data sent and the line shift below is for formatting the terminal output
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
	start_time = time.time()								# Define start time
	total_data_received = 0									# Initialize the total_data_received variable to track how much data has been received

	try:										
		while True:
			data = connection.recv(1000)					# define variable data which receives data chunks in 1000 bytes in the server
			total_data_received += len(data)    			# We must have len() because data is a bytes object and len() returns the length of the object i.e byte size

			if b'BYE' in data:					
				connection.send(b'ACK')						# If we receive a 'BYE' String from the client, return an 'ACK' String and break out
				break

			if not data:									# If we don't receive data we also need to break out of the while loop
				break

	except Exception as e:									# Throw an Exception if the server can't handle the connection
		print(f"An error occurred while handling the connection: {e}")

	connection.close()										# Close connection as soon as we don't need it anymore

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
	
	while True:
		connection, address = server_socket.accept()													# Create a connection socket representing the connection between client and server and create tuple with client ip and port
		print(f"A simpleperf client with {address} is connected with server ('{ip}', {port}) \n")		# Print the info of the specific client that has connected

		# Create a new thread to handle this connection
		connection_thread = threading.Thread(target=handle_connection, args=(connection, address, unit))	# Create a thread object that will run the handle_connection() function when started
		connection_thread.start()																			# Start the thread object that was recently instantiated



# Description:
# This function is responsible for sending data to the server in parallel connections, either using the number of bytes, the time interval or a defined duration of time.
# It prints out statistics about the transfer at specified intervals if an interval is defined. It is called on as a thread by the run_client() function which creates a thread object which
# runs as a single thread or multi threads depending on the specified number of parallel connections defined in the client terminal. It starts off by creating a client socket which connects
# to a given server ip and port and prints out information about the newly formed connections in parallel or not. Then depending on the parameters provided into the client terminal, the script
# will jump into the numbytes function, the interval function or it will just print out the total sumamry statistic if neither. It will keep sending chunks of 1000 byte data to the server
# side until the time elapses, where it will send a 'BYE' String to the server and subsequently receive an acknowledgement 'ACK' string. It will then calculate the elapsed time, set it to 1 if
# the timer is less than one, because if it's very small the program may interpret the very small time elapsed as 0 and dividing by 0 is undefined. After formatting the code, it will then 
# print out the summary statistic.
# Arguments:
# server_ip: holds the ip address of the server using the IPv4 address family. If not specified by the -b flag, the default server_ip is 127.0.0.1 which is the ip of the local machine itself.
# port: port number of the server between 1024 and 65535. If not specified by the -p flag, the default port is 8088.
# duration: is the amount of time in seconds defined by the -t flag which defines how long we want the connection to send information in bytes. If not specified, default duration is 25 seconds.
# unit: is the format that we define by the -f flag, it has to either be 'B', 'KB' or 'MB'.
# interval: defines how long each interval being printed out in seconds.
# numbytes: defines the total number of bytes that will be sent to the server.
# connection: indicates the id of the parallel connection.
# connection_thread: this variable holds the handle for the parallel connection.
# start_time: is time.time() which shows time elapsed after January 1, 1970, 00:00:00, in this case we start the timer from when the function is called.
# client_socket: this is the client socket object that is created from the parallel_send_data function which defines a specific connection to the server. It utilizes the TCP transport protocol and IPv4 address family.
# Returns:
# Void. The function doesn't return anything.

def parallel_send_data(server_ip, port, duration, unit, interval, numbytes, connection):
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)						# Crete a client socket utiziling IPv4 and TCP transport protocol

	client_socket.connect((server_ip, port))												# Connect to the server interface that we opened with -s
	client_ip = client_socket.getsockname()[0]												# This will return the first element in the tuple which contains the ip of the client socket
	client_port = client_socket.getsockname()[1]											# This will return the second element in the tuple which contains the port of the client socket
	print(f"Client {client_ip}:{client_port} connected with server {server_ip} {port}")		# Print info about the specific connection

	time.sleep(0.01) 																		# To make sure that all the info about the parallel connections get printed before the header
	if connection == 1:																		# We want to make sure that the header is only printed once when we run in parallel
		print() 				
		print("{:<20}{:<20}{:<20}{:<20}".format("ID", "Interval", "Transfer", "Bandwidth"))	# Only print the header with the first connection to prevent multiple printings of the header
	
	start_time = time.time()																# Initiate start time
	if numbytes:																			# If we defined the -n flag, go into the first if statement
		total_data_sent = send_data_with_numbytes(client_socket, numbytes)
	elif interval:																		    # If we defined the -i flag, go into the elif statement
		total_data_sent = print_interval_stats(client_socket, server_ip, port, time.time(), duration, interval, unit)
	else:																				    # If neither are defined, go into the else
		total_data_sent = 0																	# initiate total_data_sent to 0
		data_chunk = b'\0' * 1000															# data chunk variable to make sure each .send() call sends 1000 bytes at a time

		while time.time() - start_time < duration:											# As long as time elapsed isn't greater than duration, we keep sending data chunks
			sent = client_socket.send(data_chunk)											# send 1000 bytes to the server side each iteration
			total_data_sent += sent															# add the total amount to the total_data_sent variable

	client_socket.send(b'BYE')																# Once done with sending data to the server, send a 'BYE' String to the server
	ack = client_socket.recv(1024)															# Sending a 'BYE' String triggers a response which should contain 'ACK' String.

	if ack == b'ACK':																		# If we received the String, go into the if statement
		elapsed_time = time.time() - start_time												# define elapsed time variable
		if elapsed_time < 1:																# If the elapsed time is less than 1, give elapsed_time value 1
			elapsed_time = 1																
		sent_data = total_data_sent / format_to_bytes(1, unit)								# Convert the received data into the specified format
		bandwidth_Mbps = (total_data_sent / format_to_bytes(1, "MB") * 8)						# Convert bandwidth from megabytes to megabits
		bandwidth = bandwidth_Mbps / elapsed_time												# Get the average bandwidth
		
		# Print the summary statistic for each connection
		print("{:<20}{:<20}{:<20}{:<20}".format(f"{server_ip}:{port}", f"0.0 - {elapsed_time:.2f}", f"{int(sent_data)} {unit}", f"{bandwidth:.2f} Mbps"))

	client_socket.close()																	# Close the client socket connection when done


# Description:
# This function is responsible for running the client and starts by connecting to the specified server ip and port. It then prints out information about the established connection.
# Depending on the arguments passed into the function, it creates multiple thread objects running the parallel_send_data function which handles the data transfer to the server
# through a specified number of parallel connections. It keeps track of all the threads that are created and starts them using the .start() method. After that, the method waits for
# all the threads to finish executing using the .join() method.
# Arguments:
# server_ip: holds the ip address of the server using the IPv4 address family. If not specified by the -b flag, the default server_ip is 127.0.0.1 which is the ip of the local machine itself.
# port: port number of the server between 1024 and 65535. If not specified by the -p flag, the default port is 8088.
# duration: is the amount of time in seconds defined by the -t flag which defines how long we want the connection to send information in bytes. If not specified, default duration is 25 seconds.
# unit: is the format that we define by the -f flag, it has to either be 'B', 'KB' or 'MB'.
# interval: defines how long each interval being printed out in seconds.
# parallel: defines the number of parallel connections defined in the client terminal. Each parallel connection creates a thread object running the parallel_send_data function. If not specified, default is 1.
# numbytes: defines the total number of bytes that will be sent to the server.
# Returns:
# Void. The function doesn't return anything.

def run_client(server_ip, port, duration, unit, interval, parallel, numbytes):
	# Print out info about the client connection to the server
	print("---------------------------------------------")
	print(f"Simpleperf client connecting to server {server_ip}, port {port}")
	print("---------------------------------------------")
	print()

	threads = []								# Initialize empty list to manage thread objects

	# Create thread objects using the Thread() constructor from the "threading" module and run each one in the for loop
	for i in range(parallel): 											
		t = threading.Thread(target=parallel_send_data, args=(server_ip, port, duration, unit, interval, numbytes, i + 1))	# target parameter states which function should be called when thread starts running
		t.start() 																											# Start the thread after defining it
		threads.append(t) 																									# Add it to the threads array list

	for t in threads: 							# WAit for all the threads to finish executing before proceeding with the rest of the program
		t.join() 								# the join() method ensures that all the threads have been executed before we move onto the next line of the run_client() code
												# In this case it is nothing, because there is no more code in the run_client() method after the "t.join()" method call in the previous line

# Description:
# This function is responsible for parsing the command-line arguments passed to the program and returns an object containing the values of the arguments. First it accesses the argparse python
# module and we instantiate a parser object of the class ArgumentParser. We add specific arguments line after line after that. The arguments could be "-s" or "--server" to start the server
# and when the parser encounters this, it stores a boolean "True" when it is encountered. Other options could be type = "str" indicating a string to be expected. It could also contain "default"
# which is the value the program will default to the specified argument if none is provided in the terminal. Finally, by running -h, the terminal will return simple documentation about 
# the script and what the arguments can be. Below are if statements that handles exceptions for illegal arguments in the terminal and exits the program with status code 1, which implies
# an error. Finally we have input validation for the numbytes argument, which is handled by regular expression. Here we have to import the re module which includes the .match() method
# which takes in a String as the first argument which is a pattern which is what the args.numbytes String will match itself with. The first part of the String "r"(\d+)([a-zA-Z]+)"" is 
# (\d+) which means that the first part of the string can be one or more digits (0-9) and this will be returned as a separate object. The second part is ([a-zA-Z]+) which will also return
# a second object which means that the second part of the String in args.numbytes will consist of a variety of letters both big and small in the alphabet a-zA-Z. The second argument is
# the String, in this case "args.numbytes" that we want to match and the third argument "re.I" means ignore case and that we should treat uppercase and lowercase letters as equivalent.
# If the input matches the regex, we unpack the match.groups() tuple into two variables first one being "number value" and the second variable being "unit". We then test the unit to check
# if the unit is either B, KB or MB and if not, raise an error. If the whole input in the command line doesn't match regex, raise exception. Finally return the complete args object.
# Arguments:
# None
# Returns:
# An object containing the values of the arguments parsed from the command-line. The object contains the following attributes:
# - server: True if the program should run in server mode, False otherwise
# - client: True if the program should run in client mode, False otherwise
# - bind: the IP address of the server's interface, default is "127.0.0.1"
# - ip: the server IP address, default is "127.0.0.1"
# - port: the port number to use for the connection, default is 8088
# - time: the duration of the data transfer in seconds, default is 25
# - format: the format in which to display the data transfer rate, can be "B", "KB", or "MB", default is "MB"
# - interval: the interval at which to display statistics in seconds, default is None
# - parallel: the number of parallel connections to use for the data transfer, default is 1
# - numbytes: the total number of bytes to transfer, specified as a string with a number and unit (e.g. "10MB"), default is None
# An example could be: args = { "server": False, "client": True, 'bind': '192.168.1.10', "ip": "192.168.1.100", "port": 8088, "time": 30, "format": "MB", "interval": 5, "parallel": 1, "numbytes": none } 

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

	args = parser.parse_args()														# Parses arguments from the terminal so that we can access the arguments in the script

	if args.port not in range(1024, 65536):											# terminate program and print error if the port number is outside [1024, 65535]
		print("Error: port number must be in the range between 1024 and 65535")
		sys.exit(1)

	if args.time <= 0:																# terminate program and print error if the -t flag is not a positive integer
		print("Error: -t flag must be greater than 0")
		sys.exit(1)

	if args.interval is not None and args.interval <= 0:  							# terminate program and print error if the -i flag is not a positive integer
		print("Error: interval must be a positive integer")
		sys.exit(1)

	if args.parallel not in range(1,6):												# terminate program and print error if the -p flag is not within [1, 5]
		print("Error: the number of parallel connections can only be between 1 to 5")
		sys.exit(1)

	if args.numbytes:
		match = re.match(r"(\d+)([a-zA-Z]+)", args.numbytes, re.I)					# Match the input of -n to the regular expression

		if match:
			num_bytes_value, num_bytes_unit = match.groups()						# If there is a match, unpack the tuple from .groups() into two variables, the first number value and the second one, unit

			num_bytes_value = int(num_bytes_value)									# Convert the matched number to an int

			if num_bytes_unit.upper() not in ["B", "KB", "MB"]:						# Check if the unit is valid (B, KB, or MB)
				raise ValueError("Invalid unit. Please use B, KB, or MB.")			# Raise exception if the unit variable isn't B, KB or MB

			args.numbytes = format_to_bytes(num_bytes_value, num_bytes_unit)		# Convert the number value to bytes

		else:
			# If the input doesn't match the expected pattern, raise an error
			raise ValueError("Invalid format. Please provide the input in the format: <number><unit>, For example: 10MB")
	return args 																	# We return the final args object

# Description:
# This function takes in a value and a unit as arguments and returns the value in bytes. It is used to convert values of different sizes (e.g. KB, MB) into bytes, which is the unit used in the
# program to measure the amount of data transferred. A ValueError is raised if an invalid unit is provided.
# Arguments:
# value: an integer representing the value to be converted
# unit: a string representing the unit of the value (e.g. "B", "KB", "MB")
# Returns:
# An integer representing the converted value in bytes.

def format_to_bytes(value, unit):
	if unit == "B":												# If the unit is "B" then we are already at bytes
		return value
	elif unit == "KB":											# If unit is "KB" then we need to multiply by 1000 to convert to bytes
		return value * 1000
	elif unit == "MB":
		return value * 1000 * 1000								# If unit is "BB" then we need to multiply by 1000000 to convert to bytes
	else:
		raise ValueError(f"Invalid unit: {unit}")				# Raise error if unit is invalid

if __name__ == "__main__":
	args = parse_arguments()									# Code starts at main and we start off by defining the args object 

	# If both -c and -s have been implemented in the terminal, handle error
	if args.server and args.client:							
		print("Error: you must run either in server or client mode, not both")
		sys.exit(1)
	elif args.client:											# If we only have -c then we invoke the client
		run_client(args.ip, args.port, args.time, args.format, args.interval, args.parallel, args.numbytes)
	elif args.server:											# If we only have -s then we invoke the server
		run_server(args.bind,args.port,args.format)
	else:
		print("Error, you must select server or client mode")	# If neither of those things, handle error
		sys.exit(1)