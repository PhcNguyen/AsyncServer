
# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import json
import socket

from socket import socket as Socket
from concurrent.futures import ThreadPoolExecutor

from models import settings



class Networks(settings.Networks):
    def __init__(self, host: str, port: int, handle_data):
        self.server_address = (host, port)
        
        self.handle_data = handle_data
        self.client_connections = []
        self.message_callback = None
        self.executor = ThreadPoolExecutor(max_workers=50)
        self.running = True

    def start(self):
        """Khởi động server và lắng nghe các kết nối đến."""
        try:
            self.server_socket = Socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.settimeout(60)


            
            self.server_socket.bind(self.server_address)
            self.server_socket.listen()
            self._notify(f'Server đang lắng nghe tại {self.server_address}.')
            self.accept_connections()
        except OSError as e:
            self._notify_error("Lỗi hệ điều hành (OSError): " + str(e))
        except ValueError as e:
            self._notify_error("Giá trị không hợp lệ (ValueError): " + str(e))
        except Exception as error:
            self._notify_error("Lỗi không xác định: " + str(error))

    def stop(self):
        """Dừng server và đóng tất cả các kết nối."""
        try:
            for conn, addr in self.client_connections:
                conn.shutdown(socket.SHUT_RDWR)
                conn.close()

            if self.server_socket.fileno() == -1:
                raise OSError("Socket đã bị đóng.")
            else:
                self.server_socket.close()

            self.running = False
            self._notify('Server stopped.')
        except OSError as e:
            self._notify_error("Lỗi hệ điều hành (OSError): " + str(e))
        except Exception as e:
            self._notify_error(f"Error during shutdown: {e}")
        finally:
            self.client_connections.clear()

    def accept_connections(self):
        """Chấp nhận các kết nối đến."""
        while self.running:
            try:
                client_socket, client_address = self.server_socket.accept()
                client_socket.settimeout(60)
                self.client_connections.append((client_socket, client_address))
                self.executor.submit(self.handle_client, client_socket, client_address)
            except socket.timeout:
                self._notify('Server socket timed out.')
            except OSError as e:
                self._notify_error(str(e))
                break
            except Exception as e:
                self._notify_error(f"Error accepting connections: {e}")
                break

    def handle_client(self, client_socket: Socket, client_address: tuple):
        """Xử lý dữ liệu từ client."""
        try:
            while True:
                try:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    self._notify_data(data)
                    client_socket.sendall(self.handle_data(client_address, data))
                except socket.timeout:
                    self._notify_data(f"Connection to {client_address} timed out.")
                    break
                except Exception as e:
                    self._notify_error(f"Error handling client {client_address}: {e}")
                    break
        finally:
            client_socket.close()
            self.client_connections = [conn for conn in self.client_connections if conn[1] != client_address]

    def set_message_callback(self, callback):
        self.message_callback = callback


    def _notify(self, message):
        if self.message_callback:
            self.message_callback(f'Notify: {message}')

    def _notify_data(self, message):
        if self.message_callback:
            self.message_callback(f'Data: {message}')

    def _notify_error(self, message):
        if self.message_callback:
            self.message_callback(f'Error: {message}')