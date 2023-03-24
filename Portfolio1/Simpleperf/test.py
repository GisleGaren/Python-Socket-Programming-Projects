import argparse
import socket
import time

def main():
    parser = argparse.ArgumentParser(description="Simpleperf Server")
    parser.add_argument("-s", "--server", action="store_true", help="Run as server")
    parser.add_argument("-p", "--port", type=int, default=5001, help="Port number to use (default: 5001)")
    args = parser.parse_args()

    if args.server:
        run_server(args.port)

def run_server(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(1)

    print("--------------------------------------------------")
    print(f"A simpleperf server is listening on port {port}")
    print("--------------------------------------------------")

    while True:
        conn, addr = server_socket.accept()
        print(f"Connected by {addr}")
        start_time = time.time()
        total_bytes_received = 0

        while True:
            data = conn.recv(1000)
            if not data:
                break
            total_bytes_received += len(data)

        end_time = time.time()
        conn.close()
        elapsed_time = end_time - start_time
        bandwidth = calculate_bandwidth(total_bytes_received, elapsed_time)
        print(f"Connection closed. Total data received: {total_bytes_received} bytes")
        print(f"Elapsed time: {elapsed_time:.2f} seconds")
        print(f"Bandwidth: {bandwidth:.2f} Mbps")

def calculate_bandwidth(bytes_received, time_elapsed):
    bits_received = bytes_received * 8
    bandwidth = (bits_received / time_elapsed) / 1000000
    return bandwidth

if __name__ == "__main__":
    main()
