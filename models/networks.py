
# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import json
import socket

from socket import socket as Socket
from concurrent.futures import ThreadPoolExecutor

from models import settings
from models.mysqlite import SQLite



class Networks(settings.Networks):
    def __init__(self, host: str, port: int):
        self.server_address = (host, port)
        
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
                    client_socket.sendall(handle_data(client_address, data))
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



def handle_data(client_address: tuple, data: dict) -> bytes:
    """Xử lý dữ liệu từ client và trả về kết quả."""
    # Nếu data là bytes, giải mã và chuyển sang JSON
    if isinstance(data, bytes):
        try:
            data = data.decode('utf-8')
            data = json.loads(data)
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            return f"Error decoding data: {e}".encode()

    # Kiểm tra định dạng data có đúng là dict không
    if not isinstance(data, dict):
        return "Invalid data format".encode()

    # Xử lý các hành động từ client
    action = data.get("action")
    
    if action == "register":
        username = data.get("username")
        password = data.get("password")
        if not username or not password:
            return "Missing username or password".encode()
        
        if sqlite3.register(username, password):
            return json.dumps({"status": "success", "message": "Register success"}).encode()
        else:
            return json.dumps({"status": "error", "message": "Register failed"}).encode()

    elif action == "login":
        username = data.get("username")
        password = data.get("password")
        if not username or not password:
            return "Missing username or password".encode()
        
        if sqlite3.login(username, password):
            return json.dumps({"status": "success", "message": "Login success"}).encode()
        else:
            return json.dumps({"status": "error", "message": "Login failed"}).encode()

    elif action == "message":
        sender = data.get("sender")
        receiver = data.get("receiver")
        message = data.get("message")
        if not sender or not receiver or not message:
            return "Missing sender, receiver, or message".encode()
        
        return sqlite3.handle_message(sender, receiver, message)

    elif action == "friend_request":
        sender = data.get("sender")
        receiver = data.get("receiver")
        if not sender or not receiver:
            return "Missing sender or receiver".encode()
        
        return sqlite3.handle_friend_request(sender, receiver)

    elif action == "accept_friend":
        sender = data.get("sender")
        friend = data.get("friend")
        if not sender or not friend:
            return "Missing sender or friend".encode()

        return sqlite3.handle_accept_friend(sender, friend)

    elif action == "block":
        blocker = data.get("blocker")
        blockee = data.get("blockee")
        if not blocker or not blockee:
            return "Missing blocker or blockee".encode()

        return sqlite3.handle_block_user(blocker, blockee)

    else:
        return "Invalid action".encode()



if __name__ == '__main__':
    sqlite3 = SQLite(SQLite.db_path)