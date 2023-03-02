#import socket module
# Write http://10.47.24.207:12000/Oblig/index.html depending on the ip address.
from socket import *
import socket # We imported socket so that we can get the socket.gethostbyname(socket.gethostname()) code so that we don't need to hardcode the private ip address
import sys # In order to terminate the program
import _thread as thread

#Prepare a sever socket
#Write your code here
# Create a server socket that client sockets can connect to. AF_INET means that we are dealing with ipv4 connections and sock_stream means that we are connecting via TCP protocol

def handleClient(connection):
	"""
	a client handler function 
	"""
	try:
		message = connection.recv(4096).decode()
		print(message)
		filename = message.split()[1]
		f = open(filename[1:])
		outputdata = f.read()
		f.close() 
		responseHTTP = "HTTP/1.1 200 OK \r\nContent-Type: text/html\r\nContent-Lenght: " +str(len(outputdata)) + "\r\n\r\n"
		connection.send(responseHTTP.encode()) 
		for i in range(0, len(outputdata)):
			connection.send(outputdata[i].encode())
			connection.send("\r\n\r\n".encode()) 
			connection.close()
	except IOError:
		connection.send(b'HTTP/1.1 404 Not Found\r\n\r\n')
		connection.send(b'<html><head></head><body><h1>404 Not Found</h1></body></html>\r\n')
		connection.close()

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

	while True:
		try:
			connectionSocket, addr = serverSocket.accept()
			print("Server connected by " + addr)
			thread.start_new_thread(handleClient, (connectionSocket,))
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

#End of your code
if __name__ == '__main__':
	main()
serverSocket.close()