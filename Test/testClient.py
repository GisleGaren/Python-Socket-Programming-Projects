import socket

HEADER = 64
PORT = 12000
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET,socket.SOCK_STREAM) # Må koble til 
client.connect(ADDR)

def send(msg):
    message = msg.encode(FORMAT) # This is because when we send messages, we need to encode them into bytes format. So we encode the string "msg" to bytes.
    msg_length = len(message) # This line will turn the String length into an int so "Hello" will return 5
    send_length = str(msg_length).encode(FORMAT) # This will turn the int back into a String.
    send_length += b' ' * (HEADER - len(send_length)) # This line will subtract the send_length from HEADER and multiply it by the byte space b' ' and
    # eventually add it 
    client.send(send_length)
    client.send(message)

send("Hello World!")

send(DISCONNECT_MESSAGE)