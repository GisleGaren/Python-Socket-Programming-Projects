import socket
import sys
import time
import argparse

def run_server(port, unit):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', port))
    server_socket.listen(1)

    print("---------------------------------------------")
    print(f"A simpleperf server is listening on port {port}")
    print("---------------------------------------------")

    while True:
        connection, address = server_socket.accept()
        print(f"Connected to {address}")

        start_time = time.time()
        total_data_received = 0

        try:
            while True:
                data = connection.recv(1000)
                total_data_received += len(data)

                if data == b'FINISH':
                    connection.send(b'ACK')
                    break

                if not data:
                    break
        finally:
            connection.close()

        elapsed_time = time.time() - start_time
        received_data = total_data_received / format_to_bytes(1, unit)
        bandwidth = received_data / elapsed_time

        print(f"Received {received_data:.2f} {unit} in {elapsed_time:.2f} seconds")
        print(f"Bandwidth: {bandwidth:.2f} {unit}/s")
        print("---------------------------------------------")

        received_data_mb = total_data_received / format_to_bytes(1, "MB")
        bandwidth_mbps = (received_data_mb * 8) / elapsed_time

        print(f"{'ID':<15}{'Interval':<15}{'Received':<15}{'Rate':<15}")
        print(f"{address[0]}:{address[1]:<15}{0.0}-{elapsed_time:.2f:<15}{int(received_data_mb)} MB{:<15}{bandwidth_mbps:.2f} Mbps")
        print("---------------------------------------------")

def run_client(server_ip, port, duration, interval=None):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, port))
    print("---------------------------------------------")
    print(f"A simpleperf client connecting to server {server_ip}, port {port}")
    print("---------------------------------------------")

    start_time = time.time()
    total_data_sent = 0
    data_chunk = b'\0' * 1000
    interval_start_time = start_time

    if interval:
        print("Table ID Interval Transfer Bandwidth")
    while time.time() - start_time < duration:
        sent = client_socket.send(data_chunk)
        total_data_sent += sent

        if interval and (time.time() - interval_start_time >= interval):
            elapsed_interval = time.time() - interval_start_time
            interval_bandwidth = sent / elapsed_interval / 1000 / 1000 * 8
            interval_start_time = time.time()

            print(f"{server_ip}:{port} {elapsed_interval:.1f} - {time.time() - start_time:.1f} {sent / 1000 / 1000:.2f} MB {interval_bandwidth:.2f} Mbps")

    client_socket.send(b'FINISH')
    ack = client_socket.recv(1024)

    if ack == b'ACK':
        elapsed_time = time.time() - start_time
        bandwidth = total_data_sent / elapsed_time / 1000 / 1000 * 8

        print(f"----------------------------------------------------")
        print(f"{server_ip}:{port} 0.0 - {elapsed_time:.1f} {total_data_sent / 1000 / 1000:.2f} MB {bandwidth:.2f} Mbps")
        print("---------------------------------------------")

    client_socket.close()


# Function to parse command line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description="A simple network throughput measurement tool")
    parser.add_argument("-s", "--server", action="store_true", help="Run in server mode")
    parser.add_argument("-c", "--client", action="store_true", help="Run in client mode")
    parser.add_argument("-I", "--ip", type=str, default="127.0.0.1", help="Server IP address (default: 127.0.0.1)")
    parser.add_argument("-p", "--port", type=int, default=8088, help="Port number (default: 8088)")
    parser.add_argument("-t", "--time", type=int, default=25, help="Duration in seconds (default: 25)")
    parser.add_argument("-f", "--format", type=str, choices=["B", "KB", "MB"], default="MB", help="Summary format (default: MB)")
    parser.add_argument("-i", "--interval", type=int, help="Print statistics per interval seconds")
    parser.add_argument("-P", "--parallel", type=int, default=1, choices=range(1, 6), help="Number of parallel connections (default: 1)")
    parser.add_argument("-n", "--numbytes", type=str, help="Number of bytes to transfer (e.g., 100B, 1KB, 10MB)")

    args = parser.parse_args()

    if args.numbytes:
        num_bytes_value = int(args.numbytes[:-2])
        num_bytes_unit = args.numbytes[-2:]
        args.numbytes = format_to_bytes(num_bytes_value, num_bytes_unit)

    return args

def format_to_bytes(value, unit):
    if unit == "B":
        return value
    elif unit == "KB":
        return value * 1000
    elif unit == "MB":
        return value * 1000 * 1000
    else:
        raise ValueError(f"Invalid unit: {unit}")

if __name__ == "__main__":
    args = parse_arguments()

    if args.server:
        run_server(args.port, args.format)
    elif args.client:
        run_client(args.ip, args.port, args.time, args.interval)
    else:
        print("Error: you must run either in server or client mode")
        sys.exit(1)
