import socket
import threading

HEADER = 64
PORT = 12000
# SERVER = "172.24.128.1" Is one way of getting the hostname() by hardcoding it via terminal writing "ipconfig" The issue is that you will have to
# hard code the new local ipv4 address everytime we connect to a new network. The code in line 7 is much more efficient.
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT) # Address
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
    
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR) # Now this means that we have bound this socket to this address with PORT 12000 as well as our local ipv4 address

def handleClient(conn, addr): # This function will handle all threads, in other words, all connections from client to server and back.
    print(f"[NEW CONNECTION] {addr} connected")

    connected = True
    while connected: 
        msg_length = conn.recv(HEADER).decode(FORMAT) # This is a blocking line of code so that we will not pass this line until we receive a message from the client. Important so that we are not blocking other clients from connecting.
        # Everytime we send a msg we need to decode it from bytes format to string utf-8 format.
        if(msg_length): # If there is content in this message:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT) # So here we essentially take in the String and we convert it into its exact length and put it back into conn.recv so that we don't use
            #more space than we need.

            if(msg == DISCONNECT_MESSAGE):
                connected = False
            print(f"[{addr}] {msg}")
            conn.send("Msg received".encode(FORMAT)) # We addded this line if we wanted to send a message from the server to the client
    
    conn.close()

def start(): # This handles new connections and distributes them to where they need to go contra handleClient, which handles individual specific connections.
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True: # Loop goes to infinite and remember that conn, addr HAS to be in that order! Last time I did addr, conn and we get an error!!
        conn, addr = server.accept() # Server.accept() Will take the first connect request from the connect request queue
        # It will also wait as long if the queue is empty and will return a conn that the server can communicate with the client and an object addr containing info about the client.
        thread = threading.Thread(target = handleClient, args=(conn, addr)) # When a new connection occurs, we are going to pass that connection to handleClient() via target = handleClient
        # args is what arguments we are passing into the function.
        thread.start() 
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() -1}") # We want to see how many active connections we curerntly have and amount of threads = amount of clients connected
        # We need to include -1 because the start thread line 36 server.listen() is always running.
print("[STARTING] server is starting ...")
start() 