import socket
import sys
import time
import argparse
import threading
import multiprocessing  # Import multiprocessing

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
	print("\n----------------------------------------------------------------------------------- \n")
	return total_data_sent

def send_data_with_numbytes(client_socket, numbytes):
	total_data_sent = 0
	data_chunk = b'\0' * 1000

	while total_data_sent < numbytes:
		sent = client_socket.send(data_chunk)
		total_data_sent += sent

	return total_data_sent

# Add this new function to handle individual client connections
def handle_connection(connection, address, unit):
    start_time = time.time()
    total_data_received = 0

    try:
        while True:
            data = connection.recv(1000)
            total_data_received += len(data)

            if data == b'FINISH':
                connection.send(b'ACK')
                break

            if not data:
                break
    finally:
        connection.close()

    elapsed_time = time.time() - start_time
    received_data = total_data_received / format_to_bytes(1, unit)
    bandWidth_MB = (total_data_received / format_to_bytes(1, "MB") * 8)
    bandwidth = bandWidth_MB / elapsed_time

    print("{:<20}{:<20}{:<20}{:<20}".format("ID", "Interval", "Received", "Rate"))
    print("{:<20}{:<20}{:<20}{:<20}".format(f"{address[0]}:{address[1]}", f"0.0 - {elapsed_time:.2f}", f"{int(received_data)} {unit}", f"{bandwidth:.2f} Mbps"))

def run_server(ip, port, unit):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip, port))
    server_socket.listen(5)

    print("---------------------------------------------")
    print(f"A simpleperf server is listening on {ip}:{port}")
    print("---------------------------------------------")

    while True:
        connection, address = server_socket.accept()
        print(f"A simpleperf client with {address} is connected with server ('{ip}', {port}) \n")

        # Create a new thread to handle this connection
        connection_thread = threading.Thread(target=handle_connection, args=(connection, address, unit))
        connection_thread.start()

def parallel_send_data(server_ip, port, duration, unit, interval, numbytes, connection):
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	client_socket.connect((server_ip, port))

	print(connection)
	if numbytes:
		total_data_sent = send_data_with_numbytes(client_socket, numbytes)
	elif interval:
		total_data_sent = print_interval_stats(client_socket, server_ip, port, time.time(), duration, interval, unit)
	else:
		total_data_sent = 0
		data_chunk = b'\0' * 1000

		start_time = time.time()
		while time.time() - start_time < duration:
			sent = client_socket.send(data_chunk)
			total_data_sent += sent

	print(f"{connection} has transferred {total_data_sent} bytes") # For å sjekke hvor mange bytes hver connection sender
	client_socket.send(b'FINISH')
	ack = client_socket.recv(1024)

	if ack == b'ACK':
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

	print("{:<20}{:<20}{:<20}{:<20}".format("ID", "Interval", "Transfer", "Bandwidth"))

	processes = []
	
	# Create a thread object using the Thread() constructor from the "threading" module 
	for i in range(parallel): # target parameter states which function should be called when thread starts running
		p = multiprocessing.Process(target=parallel_send_data, args=(server_ip, port, duration, unit, interval, numbytes, i + 1))
		p.start() # Start the thread after defining it
		processes.append(p) # Add it to the array list

	for p in processes: # WAit for all the threads to finish executing before proceeding with the rest of the program
		p.join() # the join() method ensures that all the threads have been executed before we move onto the next line of the run_client() code.
		# In this case it is nothing, because there is no more code in the run_client() method after line 141.


# Function to parse command line arguments
def parse_arguments():
	parser = argparse.ArgumentParser(description="A simple network throughput measurement tool")
	parser.add_argument("-s", "--server", action="store_true", help="Run in server mode")
	parser.add_argument("-c", "--client", action="store_true", help="Run in client mode")
	parser.add_argument("-b", "--bind", type=str, default="127.0.0.1", help="Select the ip address of the server's interface (default: 127.0.0.1)")
	parser.add_argument("-I", "--ip", type=str, default="127.0.0.1", help="Server IP address (default: 127.0.0.1)")
	parser.add_argument("-p", "--port", type=int, default=8088, choices=range(1024, 65536), help="Port number (default: 8088)")
	parser.add_argument("-t", "--time", type=int, default=25, help="Duration in seconds (default: 25)")
	parser.add_argument("-f", "--format", type=str, choices=["B", "KB", "MB"], default="MB", help="Summary format (default: MB)")
	parser.add_argument("-i", "--interval", type=int, help="Print statistics per interval seconds")
	parser.add_argument("-P", "--parallel", type=int, default=1, choices=range(1, 6), help="Number of parallel connections (default: 1)")
	parser.add_argument("-n", "--numbytes", type=str, help="Number of bytes to transfer (e.g., 100B, 1KB, 10MB)")

	args = parser.parse_args()

	if args.port not in range(1024, 65536):
		print("Error: port number must be in the range between 1024 and 65536")
		sys.exit(1)

	if args.time <= 0:
		print("Error: -t flag must be greater than 0")
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