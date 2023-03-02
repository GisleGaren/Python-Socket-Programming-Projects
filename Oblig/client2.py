import sys
from socket import *

# Get command line arguments
server_host = sys.argv[1] # sys.argv[1] is a list that contains arguments passed in the terminal. 
server_port = int(sys.argv[2])
filename = sys.argv[3]

# Create TCP socket and connect to server
client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect((server_host, server_port))

# Send GET request to server
request = f"GET /{filename} HTTP/1.1\r\nHost: {server_host}\r\n\r\n"
print(request)
try:
    client_socket.send(request.encode())
except:
    print("Error sending GET Request to the server. Please try again later...")

try:
    # Receive response from server
    response = client_socket.recv(4096)
    # Print server response
    print(response.decode())
except:
    print("Error receiving response from the server. Socket closed")
    sys.exit()

# Close socket
client_socket.close()