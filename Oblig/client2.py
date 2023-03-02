import sys
from socket import *

# GET arguments from the terminal. When we want to run client2.py, we need to pass some arguments into the terminal to pass that as a GET request to the server.
# Our request line should look something like: python3 client2.py 10.47.24.207 12000 Oblig/index.html @Oslomet
server_host = sys.argv[1] # sys.argv[1] is the first parameter that is the server host. This changes from time to time, which is why I made sure that the server prints this out in the terminal when it starts up.
server_port = int(sys.argv[2]) # the second parameter belongs to the port which will always be 12000.
filename = sys.argv[3] # The final one is the file name which is Oblig/index.html which is important to add the whole directory or else the program is unable to locate the file.

# Create client socket and connect it to the server socket with the same host address (ipv4) and port number 12000.
client_socket = socket(AF_INET, SOCK_STREAM) # Create a client socket using ipv4 and TCP transportation.
client_socket.connect((server_host, server_port)) # We will connect to a server socket which will create (on the server side) a socket representing that specific connection.

# Send GET request to server using the client socket. This will look something like: GET /Oblig/index.html HTTP/1.1  Host: 10.47.24.207
request = f"GET /{filename} HTTP/1.1\r\nHost: {server_host}\r\n\r\n" 
print(request)
try:
    client_socket.send(request.encode())
except:
    print("Error sending GET Request to the server. Please try again later...")
try:
    # Without dicing up the bytes, I get an error in the terminal.
    # The following code receives a response from the server in the form of bytes and appends them to the response byte string.
    response = b'' 
    while True: # The while loop keeps running to keep continuing to receive data until there is no more data to receive.
        data = client_socket.recv(4096)
        if not data: # If no more data to receive, then break out of the loop.
            break 
        response += data
    
    # Print server response
    print(response.decode()) 
except:
    print("Error receiving response from the server. Socket closed")
    sys.exit()

# Close socket
client_socket.close()

