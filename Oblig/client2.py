import sys
from socket import *

# GET arguments from the terminal. When we want to run client2.py, we need to pass some arguments into the terminal to pass that as a GET request to the server.
# Our request line should look something like: python3 client2.py 10.47.24.207 12000 Oblig/index.html
server_host = sys.argv[1] # sys.argv[1] is the first parameter that is the server host. This changes from time to time, which is why I made sure that the server prints this out in the terminal when it starts up.
server_port = int(sys.argv[2]) # the second parameter belongs to the port which will always be 12000.
filename = sys.argv[3] # The final one is the file name which is Oblig/index.html which is important to add the whole directory or else the program is unable to locate the file.

# Create TCP socket and connect to server
client_socket = socket(AF_INET, SOCK_STREAM) # Create a client socket using ipv4 and TCP transportation.
client_socket.connect((server_host, server_port)) # We will connect to a server socket which will create (on the server side) a socket representing that specific connection.

# Send GET request to server
request = f"GET /{filename} HTTP/1.1\r\nHost: {server_host}\r\n\r\n" 
print(request)
try:
    client_socket.send(request.encode())
except:
    print("Error sending GET Request to the server. Please try again later...")

try:
    # Receive response from server
    # This was the code that I needed 
    response = b''
    while True:
        data = client_socket.recv(4096)
        if not data:
            # No more data to receive
            break
        response += data
    
    # Print server response
    print(response.decode())
except:
    print("Error receiving response from the server. Socket closed")
    sys.exit()

# Close socket
client_socket.close()

