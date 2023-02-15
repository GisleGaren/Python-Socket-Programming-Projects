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

#this is too keep all the newly joined connections! 
all_client_connections = []

def now():
	"""
	returns the time of day
	"""
	return time.ctime(time.time())

def handleClient(connection, addr):
	"""
	a client handler function 
	"""
	#this is where we broadcast everyone that a new client has joined
	print(f"[NEW CONNECTION] {addr} connected")
	### Write your code here ###

	# append this this to the list for broadcast
	all_client_connections.append(connection)
	# create a message to inform all other clients 
	# that a new client has just joined.
	message = f"New client joined from: {addr}"
	### Your code ends here ###

	while True: # A loop that goes on until we manually shut it down
		message = connection.recv(2048).decode() 
		print (now() + " " +  str(addr) + "#  ", message)
		if (message == "exit" or not message): # If we write exit in the terminal, then the client will close the connection it previously established.
			break # It will also break out of the loop if we simply press enter in the terminal without writing anything, so in other words an empty string.
		### Write your code here ###
		#broadcast this message to the others
		broadcast(connection, message)
		### Your code ends here ###
	connection.close()
	all_client_connections.remove(connection)

#Broadcasts a message to all clients except the client that initiated the connection which is why we have the if statement.
def broadcast(connection, message): # The connection parameter is the the client that has initiated the connection which is in the all_client_connections array.
	print ("Broadcasting") # It also takes in a message parameter which is the message to be broadcasted.
	### Write your code here ###
	for client in all_client_connections: # We go through each client that has connected to the server.
		if (client != connection): # If the current connection is not equal to the specified client in the 
			try:
				client.send(message.encode()) # If this is successful, then we send the message to every other 
			except:
				client.remove(client) # Remove the client if the send does not occur because we assume the client has disconnected or is no longer able
				# to receive any new messages. By removing the client we can avoid further errors if the same client wants to connect in the future.
	### Your code ends here ###

def main():
	"""
	creates a server socket, listens for new connections,
	and spawns a new thread whenever a new connection join
	"""
	serverPort = 12000
	server_ip = socket.gethostbyname(socket.gethostname())
	serverSocket = socket.socket(AF_INET,SOCK_STREAM)
	try:
		# Use the bind function wisely!
		### Write your code here ###
		serverSocket.bind((server_ip,serverPort))
		### Your code ends here ###
		
	except: 
		print("Bind failed. Error : ")
		sys.exit()
	serverSocket.listen(10)
	print ('The server is ready to receive')
	while True:
		### Write your code here ###
		connectionSocket, addr = serverSocket.accept()  # accept a connection
		### You code ends here ###
		 
		print('Server connected by ', addr) 
		print('at ', now())
		thread.start_new_thread(handleClient, (connectionSocket,addr)) 
	serverSocket.close()

if __name__ == '__main__':
	main()
