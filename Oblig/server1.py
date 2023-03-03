#import socket module
# Write http://10.47.24.207:12000/Oblig/index.html depending on the ip address.
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
	serverSocket.bind((server_ip, serverPort))
except:
	print("Bind failed. Error : ")
	sys.exit()
serverSocket.listen(1)
print ('The server is ready to receive')
#End of your code
while True:
	#Establish the connection print('Ready to serve...') connectionSocket, addr = 
	try:
		#Write your code here
		print("Ready to serve...")
		connectionSocket, addr = serverSocket.accept()
		#End of your code
		message = connectionSocket.recv(1024).decode() #Write your code here #End of your code 
		filename = message.split()[1] # This line splits the message by its spaces for example: "I like cats" turns into {"I", "like", "cats"}. If we do print(filename) the terminal returns "/index.html"
		f = open(filename[1:]) # [1:] will return all elements except for the first one so example "/index.html" will be "index.html" because the 0th element is ignored
		outputdata = f.read() # Write your code here #End of your code 

		#Send one HTTP header line into socket
		#Write your code here
		#Here the we are sending a message to a client indicating that the HTTP GET request method was a success which is what the status code "200" means.
		msg = "HTTP/1.1 200 OK\r\n\r\n" # It contains the message HTTP version 1.1 which is what is currently mostly in use worldwide and 200 OK meaning success.
		connectionSocket.send(msg.encode()) # Ultimately, the server tells the client that the server is ready to send file contents.
		#End of your code

		#Send the content of the requested file to the client 
		for i in range(0, len(outputdata)): 
			connectionSocket.send(outputdata[i].encode())
			print(outputdata[i]) 
		connectionSocket.send("\r\n".encode())
		connectionSocket.close()

	except IOError:
		#Send response message for file not found
    	#Write your code here
		connectionSocket.send("HTTP/1.1 404 Not Found\r\n\r\n".encode())
    	#End of your code
		
		connectionSocket.send("<html><head></head><body><h1>404 Not Found Test test</h1></body></html>\r\n".encode())
		#Close client socket
        
        #Write your code here
		connectionSocket.close()
		#End of your code
serverSocket.close()