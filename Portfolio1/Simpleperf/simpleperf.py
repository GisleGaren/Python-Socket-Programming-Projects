import socket
import sys
import time
import argparse

# To do list from 24.03.23. Check the bandwidth, is the information we are getting and sending back and forth of the right format? B, KB or MB?
# Go through the code line for line and learn what it does.

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
		bandwidth = received_data / elapsed_time

	#	print(f"Received {received_data:.2f} {unit} in {elapsed_time:.2f} seconds")
	#	print(f"Bandwidth: {bandwidth:.2f} {unit}/s")
	#	print("--------------------------------------------- \n \n ")

	#	print(f"{'ID':<15}{'Interval':<15}{'Received':<15}{'Rate':<15}")
	#	print(f"{address[0]}:{address[1]:<15}{{0.0}}-{elapsed_time:.2f:<15}{int(received_data)} MB {bandwidth:.2f} Mbps")
	#	print("---------------------------------------------")

		print("{:<20}{:<20}{:<20}{:<20}".format("ID", "Interval", "Received", "Rate"))
		print("{:<20}{:<20}{:<20}{:<20}".format(f"{address[0]}:{address[1]}", f"0.0 - {elapsed_time:.2f}", f"{int(received_data)} MB", f"{bandwidth:.2f} Mbps"))

	#	I believe I need to add connection.close() here as the task says that the server gracefully closes the connection when the above is printed.

def run_client(server_ip, port, duration):
	# Create a TCP socket
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# Connect to the server
	client_socket.connect((server_ip, port))
	print("---------------------------------------------")
	print(f"A simpleperf client connecting to server {server_ip}, port {port}")
	print("---------------------------------------------")

	start_time = time.time()
	total_data_sent = 0
	data_chunk = b'\0' * 1000

	while time.time() - start_time < duration:
		sent = client_socket.send(data_chunk)
		total_data_sent += sent

	# Send the finish/bye message
	client_socket.send(b'FINISH')

	# Wait for the acknowledgement
	ack = client_socket.recv(1024)

	if ack == b'ACK':
		elapsed_time = time.time() - start_time
		bandwidth = total_data_sent / elapsed_time / 1000 / 1000

		print(f"Sent {total_data_sent / 1000 / 1000:.2f} MB in {elapsed_time:.2f} seconds")
		print(f"Bandwidth: {bandwidth:.2f} MB/s")
		print("---------------------------------------------")

	client_socket.close()

# Function to parse command line arguments
def parse_arguments():
	parser = argparse.ArgumentParser(description="A simple network throughput measurement tool")
	parser.add_argument("-s", "--server", action="store_true", help="Run in server mode")
	parser.add_argument("-c", "--client", action="store_true", help="Run in client mode")
	parser.add_argument("-b", "--bind", type=str, default="0.0.0.0", help="Server IP address (default: 0.0.0.0)")
	parser.add_argument("-I", "--ip", type=str, default="127.0.0.1", help="Client IP address (default: 127.0.0.1)")
	parser.add_argument("-p", "--port", type=int, default=8088, help="Port number (default: 8088)")
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

def format_to_bytes(value, unit): # This function converts the units to their rightful value. So if we have MB
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

	if args.server:
		run_server(args.bind,args.port, args.format) # Default server settings would be data transfer in MegaBytes and port number 8088.
	elif args.client:
		run_client(args.ip, args.port, args.time)
	else:
		print("Error: you must run either in server or client mode")
		sys.exit(1)