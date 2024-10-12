# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import socket
from concurrent.futures import ThreadPoolExecutor

class Networks(settings.Networks):
    def __init__(self, host: str, port: int, handle_data):
        self.server_address = (host, port)
        self.handle_data = handle_data
        self.client_connections = []
        self.message_callback = None
        self.executor = ThreadPoolExecutor(max_workers=50)
        self.running = True

    def _notify(self, message):
        if self.message_callback:
            self.message_callback(f'Notify: {message}')

    def _notify_error(self, message):
        if self.message_callback:
            self.message_callback(f'Error: {message}')

    def start(self):
        """Khởi động server và lắng nghe các kết nối đến."""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(self.server_address)
            self.server_socket.listen()
            self._notify(f'Server đang lắng nghe tại {self.server_address}.')
            self.accept_connections()
        except OSError as e:
            self._notify_error("Lỗi hệ điều hành (OSError): " + str(e))
        except Exception as error:
            self._notify_error("Lỗi không xác định: " + str(error))

    def accept_connections(self):
        """Chấp nhận các kết nối đến."""
        while self.running:
            try:
                client_socket, client_address = self.server_socket.accept()
                self.client_connections.append((client_socket, client_address))
                self.executor.submit(self.handle_client, client_socket, client_address)
            except OSError as e:
                self._notify_error(str(e))
                break
            except Exception as e:
                self._notify_error(f"Error accepting connections: {e}")
                break

    def handle_client(self, client_socket, client_address):
        """Xử lý dữ liệu từ client."""
        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                self._notify(data)
                response = self.handle_data(client_address, data)
                client_socket.sendall(response)
        except Exception as e:
            self._notify_error(f"Error handling client {client_address}: {e}")
        finally:
            client_socket.close()
            self.client_connections.remove((client_socket, client_address))

    def stop(self):
        """Dừng server và đóng tất cả các kết nối."""
        self.running = False
        for conn, addr in self.client_connections:
            conn.close()
        self.server_socket.close()
        self._notify('Server stopped.')

    def set_message_callback(self, callback):
        self.message_callback = callback
