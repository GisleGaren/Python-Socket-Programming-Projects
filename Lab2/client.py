#Client side connects to the server and sends a message to everyone

import socket
import select
import sys

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# write server ip and port, and connect

### write your code here ###
serverPort = 12000
server_ip = socket.gethostbyname(socket.gethostname())
client_socket.connect((server_ip,serverPort))
### your code ends here ###

while True:

	""" we are going to use a select-based approach here because it will help
	us deal with two inputs (user's input (stdin) and server's messages from socket)
	"""
	inputs = [sys.stdin, client_socket] # This line will specify a list of input sources that will be monitored by the select() method. This select method
	# allows us to monitor multiple sockets for input, output and errors. In our case, we are only interested
	# in inputs (Two of them: sys.stdin, client_socket), no outputs, and no errors. 

	""" read the select documentations - You pass select three lists: the 
	first contains all sockets that you might want to try reading; the 
	second all the sockets you might want to try writing to, and the last 
	(normally left empty) those that you want to check for errors. """

	read_sockets,write_socket, error_socket = select.select(inputs,[],[]) # By passing inputs as the first argument, we instruct the select method to monitor both the command
	# line and the client socket for incoming data and then return a list of sockets that are ready to be read from. We store the list in read_stockets: in line 39. 
	# We use this to determine which input sources have data that can be read.

	# we check if the message is either coming from your terminal or 
	# from a server

	# This is to check which sockets have data that can be read. If socks == client_sockets, that means we are reading data from the socket,
	# whereas if we go directly to the else: in line 65, that means that we are reading from the terminal.
	for socks in read_sockets:
		if socks == client_socket:

			# receive message from client and display it on the server side 
			# also handle exceptions here if there is no message from the 
			# client, you should exit.

			### write your code here ###

			# Remember, the sock.recv(1024) method calls on the socket object 'socks' and the 1024 is the amount of data it can receive before it splices
			# the data into chunks.
			try:
				message = socks.recv(1024) # This is a BLOCKING CALL which means that the program will wait until data is received before moving onto
				# the next line of code.
			except:
				print('Disconnected from the server') # We take an exception handling in case the socket is closed on the other end (server) which means
				# that it will return an empty byte object.
				sys.exit() # We terminate the program when the socket closes and we return to the terminal.

			print(message.decode()) # When we receive the message via socks.recv(1024), the data is returned as a bytes object, because sockets transmits
			# data in binary and so we need to convert it from the bytes format to String.

			### your code ends here ###

		else:
			#takes inputs from the user
			message = sys.stdin.readline() # When we write an input in the terminal, this line will read the message and store it in the message variable as a String

			#send a message to the server
			### write your code here ###
			client_socket.send(message.encode()) # To send the message, we first need to convert the String to binary using encode(), then we are ready to send it to the server 
			# from the client via .send() and this is also A BLOCKING CALL and that the program will wait until the message has been sent until it moves on to the next line of code.

			### your code ends here ###
client_socket.close()
