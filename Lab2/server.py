"""
Server side: it simultaneously handle multiple clients
and broadcast when a client new client joins or a client
sends a message.
"""
from socket import *
import socket # We imported socket so that we can get the socket.gethostbyname(socket.gethostname()) code so that we don't need to hardcode the private ip address
import _thread as thread
import time
import sys

#this is too keep all the newly joined connections and store them as an array. 
all_client_connections = []

def now():
	"""
	returns the time of day
	"""
	return time.ctime(time.time())

# The handleclient function handles client connections and receives the address with the ip and port number as parameter, as well as the connection socket object that is created when the client connects to the server.
def handleClient(connection, addr):
	"""
	a client handler function 
	"""
	#this is where we broadcast everyone that a new client has joined
	print(f"[NEW CONNECTION] {addr} connected")

	# append function takes in the connection object which is what the main function creates through the .accept function. It represents a socket object of that specific connection and we use this object to communicate from server to client.
	all_client_connections.append(connection) # We add this new socket to the array.
	# create a message to inform all other clients that a new client has just joined.
	broadcast(connection, f"Client {addr} joined.") # We broadcast to the server and all the other clients except for the one that joined that a new client has joined the network.
	welcomeMessage = "Welcome to the chat!"
	connection.send(welcomeMessage.encode()) # In order to send the message, we first need to convert the welcome message from String to bytes format because network protocols operates on bytes.
	# The send() method operates on the specified connection socket created in main which sends the message to the same client that recently connected to the server.
	try:
		while True: # A loop that goes on and on...
			message = connection.recv(1024).decode().strip() # When we receive the message via connection.recv(1024), the data is returned as a bytes object, 
			#because sockets transmit data in binary and so we need to convert it from the bytes format to String. The strip method at the end eliminates all spaces before and after the string.
			print (now() + " " +  str(addr) + "#  ", message) # Prints the time and contents of the messages received from the client.
			if message == "exit": # If we write exit in the terminal, then the client will close the connection it previously established.
				broadcast(connection,f"{addr} has left the server")
				# connection.close()  Needed to remove these functions so that the terminal wouldn't crash                      
				# all_client_connections.remove(connection) Same with this one, I believe it is due to the exception handling which handles faulty connections.
				break # It will also break out of the loop if we simply press enter in the terminal without writing anything, so in other words an empty string.
			#broadcast this message to the others
			else:
				broadcast(connection, f"{addr}: {message}") # else we broadcast the message to everyone except for the client who sent the message with the address (ip, port) and the relevant message typed in the terminal.
	except:
		# connection.close()    This was causing an error where the terminal would keep getting refreshed and would spam line shifts.                    
		all_client_connections.remove(connection) # If the connection doesn't receive anything or is lost, we remove the connection from the array.

#Broadcasts a message to all clients except the client that initiated the connection which is why we have the if statement.
def broadcast(connection, message): # The connection parameter is the the client that has initiated the connection which is in the all_client_connections array.
	print ("Broadcasting") # It also takes in a message parameter which is the message to be broadcasted.
	for client in all_client_connections: # We go through each client that has connected to the server.
		if (client != connection): # We want to go through all the client sockets in the array and check if the right one matches the connection made from the main method.
			try:
				client.send(message.encode()) # If the client sockets in the array do not equal the one client socket that sent the message, we send the message to all the other clients.
			except:
				print("The client has been removed ") # If we are unable to send the message to some of the clients in the array, we print that the client has been removed.
				all_client_connections.remove(client) # Remove the client if the send does not occur because we assume the client has disconnected or is no longer able
				# to receive any new messages. By removing the client we can avoid further errors if the same client wants to connect in the future.

def main():
	"""
	creates a server socket, listens for new connections,
	and spawns a new thread whenever a new connection join
	"""
	serverPort = 12000  # We choose a random port that is usually not used, which are ports in the 4 digit range and above.
	server_ip = socket.gethostbyname(socket.gethostname()) # This line of code will get the hostname of a server regardless of where we have connected, so that we don't ahve to hardcode a specific ip each time.
	serverSocket = socket.socket(AF_INET,SOCK_STREAM) # Create a server socket that client sockets can connect to. AF_INET means that we are dealing with ipv4 connections and sock_stream means that 
	try:
		serverSocket.bind((server_ip,serverPort)) # This function binds the serverSocket object to the specified ip address of the local machine and the server will listen in on that ip address and specific port number 12000.
	except: 
		print("Bind failed. Error : ")   # If the serverSocket is unable to bind itself to the port and ip, it will return an error in the terminal.
		sys.exit()  # Terminate the program when an error occurs that cannot be handled properly.
	serverSocket.listen(10) # The serverSocket listens in on incoming connections from potential clients and can take upto 10 clients simultaneously, hence the paramter 10.
	print ('The server is ready to receive') # If the serverSocket successfully binds to the ip and port number. Print ready to receive.
	while True: # continuous loop
		connectionSocket, addr = serverSocket.accept()  # Is a blocking method call so that it waits until the server accepts the client connection before moving to the next line of code.
		# When the client connects, the server creates a new socket (connectionSocket) representing the connection (which is used for sending and receiving data between the client and the server) and the address of the corresponding client addr which consists of (host, port)
		print('Server connected by ', addr) # We print which address connected to server when the client connects.
		print('at ', now()) # prints out what time the client connected.
		thread.start_new_thread(handleClient, (connectionSocket,addr)) # We start a new thread that runs the handleClient() function where we pass connectionSocket and addr as arguments.
	serverSocket.close()  # This line will close the serverSocket object if we end up going out of the while loop.

if __name__ == '__main__':
	main()