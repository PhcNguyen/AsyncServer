import socket
import struct


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

    def send_data(self, data: bytes) -> None:
        """Send data to the server, prefixed with its length."""
        if not self.client_socket:
            raise ConnectionError("Not connected to the server.")

        try:
            # Xác định chiều dài dữ liệu và đóng gói nó
            data_length = len(data)
            # Sử dụng struct để đóng gói chiều dài dữ liệu (4 bytes)
            header = struct.pack('!I', data_length)  # Đóng gói chiều dài dữ liệu ở dạng big-endian

            # Gửi header và dữ liệu
            self.client_socket.sendall(header + data)
            print(f"Sent {data_length} bytes of data.")
        except Exception as e:
            print(f"Error during communication: {e}")

    def receive_data(self) -> bytes:
        """Receive data from the server."""
        if not self.client_socket:
            raise ConnectionError("Not connected to the server.")

        try:
            # Đọc chiều dài dữ liệu từ server
            header = self.client_socket.recv(4)
            if not header:
                print("No data received from server.")
                return b''

            # Giải nén chiều dài dữ liệu
            data_length = struct.unpack('!I', header)[0]

            # Đọc dữ liệu
            data = bytearray()
            while len(data) < data_length:
                chunk = self.client_socket.recv(data_length - len(data))
                if not chunk:
                    break  # Kết thúc kết nối
                data.extend(chunk)

            print(f"Received {len(data)} bytes of data.")
            return bytes(data)
        except Exception as e:
            print(f"Error during receiving data: {e}")
            return b''

    def close(self):
        """Close the connection to the server."""
        if self.client_socket:
            self.client_socket.close()
            print("Connection closed.")