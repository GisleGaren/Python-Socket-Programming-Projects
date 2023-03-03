#import socket module
# Write http://10.47.24.207:12000/Oblig/index.html depending on the ip address. Can also get the ip thorugh ipconfig in powershell
from socket import *
import socket # We imported socket so that we can get the socket.gethostbyname(socket.gethostname()) code so that we don't need to hardcode the private ip address
import sys # In order to terminate the program
serverSocket = socket.socket(AF_INET, SOCK_STREAM) 

#Prepare a sever socket
#Write your code here
serverPort = 12000  # We choose a random port that is usually not used, which are ports in the 4 digit range and above.
server_ip = socket.gethostbyname(socket.gethostname()) # This line of code will get the hostname of a server regardless of where we have connected, so that we don't ahve to hardcode a specific ip each time.
print(server_ip)
# Create a server socket that client sockets can connect to. AF_INET means that we are dealing with ipv4 connections and sock_stream means that we are connecting via TCP protocol
try:
	serverSocket.bind((server_ip, serverPort)) # This will create a server socket that binds itself to the specified port and ip and will listen to in on the port and ip address.
except:
	print("Bind failed. Error : ") # Return and exit if bind fails.
	sys.exit()
serverSocket.listen(1) # Only takes in a single client.
print ('The server is ready to receive')
#End of your code
while True:
	#Establish the connection print('Ready to serve...') connectionSocket, addr = 
	try:
		print("Ready to serve...")
		connectionSocket, addr = serverSocket.accept() # Creates two objects connectionSocket representing the connection between the specified client and the server as well as the addr object which contains the port number and ip address.
		message = connectionSocket.recv(1024).decode() 
		filename = message.split()[1] # This line splits the message by its spaces for example: "I like cats" turns into {"I", "like", "cats"}. If we do print(filename) the terminal returns "/index.html"
		f = open(filename[1:]) # [1:] will return all elements except for the first one so example "/index.html" will be "index.html" because the 0th element is ignored
		outputdata = f.read() # 

		#Send one HTTP header into the socket
		#Here the we are sending a message to a client indicating that the HTTP GET request method was a success which is what the status code "200" means.
		msg = "HTTP/1.1 200 OK\r\n\r\n" # It contains the message HTTP version 1.1 which is what is currently mostly in use worldwide and 200 OK meaning success.
		connectionSocket.send(msg.encode()) # Ultimately, the server tells the client that the server is ready to send file contents.

		#Send the content of the requested file to the client 
		for i in range(0, len(outputdata)): # This line of code will send every single character of the index.html file to the client socket.
			connectionSocket.send(outputdata[i].encode()) # Each letter is encoded so that we convert each character to bytes.
			print(outputdata[i]) # In the terminal we get something like "<" and then "!" then "D" and so on to form "<!DOCTYPE html>" then the next tag, then the other content etc...
		connectionSocket.send("\r\n".encode()) # This line creates lineshifts at the end indicating the end of the transmission.
		connectionSocket.close() # And we close the socket.
	except IOError:
		#Send response message if the file is not found in both as a string as well as a string with the html text.
		connectionSocket.send("HTTP/1.1 404 Not Found\r\n\r\n".encode())
		connectionSocket.send("<html><head></head><body><h1>404 Not Found Test test</h1></body></html>\r\n".encode())
		#Close the client socket
		connectionSocket.close()
serverSocket.close()