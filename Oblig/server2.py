#import socket module
# Write http://10.47.24.207:12000/Oblig/index.html depending on the ip address.
from socket import *
import socket # We imported socket so that we can get the socket.gethostbyname(socket.gethostname()) code so that we don't need to hardcode the private ip address
import sys # In order to terminate the program
import _thread as thread

#Prepare a server socket
# Create a server socket that client sockets can connect to. AF_INET means that we are dealing with ipv4 connections and sock_stream means that we are connecting via TCP protocol
def handleClient(connection):
	# A hybrid between the script I provided in lab2 as well as the server1.py script.
	try:
		message = connection.recv(1024).decode() # We receive the message header from the client side.
		print(message) # print to see how that message looks like. Looks similiar to GET /Oblig/index.html HTTP/1.1
		filename = message.split()[1] # Again we split the string into arrays with elements seperated by the spaces in the original string and we select the 2nd element (index 1)
		f = open(filename[1:]) # We open the local file "index.html" where the remove the backslash "/" via [1:]
		outputdata = f.read() # Read the contents and store the contents of the index.html file including tags and everything in outputdata
		f.close() # Close the file in case something happens to corrupt the contents.
		responseHTTP = "HTTP/1.1 200 OK \r\n\r\n" # Reponse header to the client that has connected indicating success.
		connection.send(responseHTTP.encode()) # Convert the message to bytes and send it to the client that connected.
		#The for loop sends out every single character in the index.html file so in our case it first sends "<" and then "!" then "D" and so on to form "<!DOCTYPE html>" then the next tag, then the other content etc...
		for i in range(0, len(outputdata)):
			connection.send(outputdata[i].encode())
		connection.send("\r\n\r\n".encode()) 
		connection.close()
	except IOError: # If all fails, we instead send an error message as a string as well as a string html file and close the connection.
		connection.send(b'HTTP/1.1 404 Not Found\r\n\r\n')
		connection.send(b'<html><head></head><body><h1>404 Not Found</h1></body></html>\r\n')
		connection.close()

# Not gonna comment too much in this as it's very similiar to lab2 and the server1.py script which is already heavily documented.
def main():
	serverSocket = socket.socket(AF_INET, SOCK_STREAM) 
	serverPort = 12000  # We choose a random port that is usually not used, which are ports in the 4 digit range and above.
	server_ip = socket.gethostbyname(socket.gethostname()) # This line of code will get the hostname of a server regardless of where we have connected, so that we don't ahve to hardcode a specific ip each time.
	print(server_ip)
	try:
		serverSocket.bind((server_ip, serverPort))
	except:
		print("Bind failed. Error : ")
		sys.exit()
	serverSocket.listen(10)
	print ('The server is ready to receive')
	# In general, we create everything that we need for the server socket with ip, tcp and port. We bind the server socket to a specified address and ip.
	while True:
		try:  # We check to see if the server socket can connect to the client socket and create a new socket representing that connection.
			connectionSocket, addr = serverSocket.accept()
			print("Server connected by ", addr)
			thread.start_new_thread(handleClient, (connectionSocket,)) # This time with multithreading.
		except IOError:
		#Send response message for file not found and we send that if we are unable to accept a connection between the client and server socket.
			connectionSocket.send("HTTP/1.1 404 Not Found\r\n\r\n".encode())
			serverSocket.close()
			connectionSocket.send("<html><head></head><body><h1>404 Not Found Test test</h1></body></html>\r\n".encode())
		#Close client socket
if __name__ == '__main__':
	main()