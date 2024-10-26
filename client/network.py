import socket
import json

class SocketManager:
    def __init__(self, host: str, port: int):
        """Initialize the socket manager with the server's host and port."""
        self.host = host
        self.port = port
        self.client_socket = None

    def connect(self):
        """Connect to the server."""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            print("Connected to the server.")
        except Exception as e:
            print(f"Error connecting to server: {e}")
            self.client_socket = None

    def send_request(self, request: dict) -> dict:
        """Send a JSON request to the server and return the JSON response."""
        if not self.client_socket:
            raise ConnectionError("Not connected to the server.")

        try:
            message = json.dumps(request)
            self.client_socket.sendall(message.encode('utf-8'))

            # Receive the response
            response = self.client_socket.recv(1024)
            return json.loads(response.decode('utf-8'))
        except Exception as e:
            print(f"Error during communication: {e}")
            return {"status": "error", "message": str(e)}

    def close(self):
        """Close the connection to the server."""
        if self.client_socket:
            self.client_socket.close()
            print("Connection closed.")
