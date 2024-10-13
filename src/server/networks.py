# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import typing
import socket
import asyncio


from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Optional, List, Tuple

from src.server.settings import NetworkSttings


MAX_CONNECTIONS = 1000  # Define your max connections


class Networks(NetworkSttings):
    def __init__(
        self, 
        host: str, 
        port: int, 
        handle_data: Callable[[tuple, bytes], bytes]
    ):
        self.server_address = (host, port)
        self.handle_data = handle_data
        self.client_connections = []
        self.message_callback = None
        self.executor = ThreadPoolExecutor(max_workers=50)
        self.running: bool = None

    def _notify(self, message):
        if self.message_callback:
            self.message_callback(f'Notify: {message}')

    def _notify_error(self, message):
        if self.message_callback:
            self.message_callback(f'Error: {message}')
    
    def set_message_callback(
        self, callback: 
        typing.Callable[[str], None]
    ):  self.message_callback = callback

    def start(self):
        """Khởi động server và lắng nghe các kết nối đến."""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(self.server_address)
            self.server_socket.listen()
            self._notify(f'Starting server at {self.server_address}.')
            self.running = True
            self.accept_connections()
        except OSError as error:
            self._notify_error("OSError: " + str(error))
        except Exception as error:
            self._notify_error("Unknown error: " + str(error))

    def accept_connections(self):
        """Chấp nhận các kết nối đến."""
        while self.running:
            if len(self.client_connections) >= MAX_CONNECTIONS:
                self._notify("Maximum connection limit reached. Rejecting new connections.")
                continue
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

    def handle_client(
        self, 
        client_socket: socket.socket, 
        client_address: tuple[str, int]
    ) -> bytes:
        """Xử lý dữ liệu từ client."""
        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                self._notify(data)
                response: bytes = self.handle_data(client_address, data)
                client_socket.sendall(response)
        except ConnectionResetError:
            self._notify_error(f"Client {client_address} forcibly closed the connection.")
        except socket.timeout:
            self._notify_error(f"Timeout on client {client_address}")
        except Exception as e:
            self._notify_error(f"Unexpected error: {e}")
        finally:
            client_socket.close()
            self.client_connections.remove((client_socket, client_address))

    def stop(self):
        """Dừng server và đóng tất cả các kết nối."""
        self.running = False
        for conn, addr in self.client_connections:
            conn.close()
        self.server_socket.close()
        self.executor.shutdown(wait=True)  # Wait for all threads to finish
        self._notify('Server stopped.')



class AsyncNetworks(NetworkSttings):
    def __init__(
        self, 
        host: str, 
        port: int, 
        handle_data: Callable[[Tuple[str, int], bytes], bytes]
    ):
        self.server_address: Tuple[str, int] = (host, port)
        self.handle_data: Callable[[Tuple[str, int], bytes], bytes] = handle_data
        self.message_callback: Optional[Callable[[str], None]] = None
        self.running: bool = False  # Khởi tạo với False
        self.client_connections: List[Tuple[asyncio.StreamReader, asyncio.StreamWriter]] = []

    def _notify(self, message: str):
        if self.message_callback:
            self.message_callback(f'Notify: {message}')

    def _notify_error(self, message: str):
        if self.message_callback:
            self.message_callback(f'Error: {message}')

    def set_message_callback(
        self, callback: Callable[[str], None]
    ):
        self.message_callback = callback

    async def start(self):
        """Start the server and listen for incoming connections asynchronously."""
        if self.running:
            self._notify_error("Server is already running.")
            return
        
        try:
            self._notify(f'Starting async server at {self.server_address}')
            self.running = True
            server = await asyncio.start_server(self.handle_client, *self.server_address)
            async with server:
                # self._notify('Server started successfully.')  # Thông báo thành công
                await server.serve_forever()
        except OSError as error:
            self._notify_error("OSError: " + str(error))
        except Exception as error:
            self._notify_error("Unknown error: " + str(error))

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle data from a client asynchronously with timeout."""
        client_address = writer.get_extra_info('peername')
        self.client_connections.append((reader, writer))
        self._notify(f"Client connected from {client_address}")

        try:
            while True:
                try:
                    data = await asyncio.wait_for(reader.read(1024), timeout=60.0)  # 60s timeout
                except asyncio.TimeoutError:
                    self._notify(f"Client {client_address} timed out.")
                    break
                
                if not data:
                    break  # Client disconnected

                response: bytes = self.handle_data(client_address, data)
                writer.write(response)
                await writer.drain()  # Ensure the data is sent
        except Exception as e:
            self._notify_error(f"Error handling client {client_address}: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
            # Xóa kết nối đã đóng
            self.client_connections = [(r, w) for r, w in self.client_connections if not w.is_closing()]

    async def stop(self):
        """Stop the server and close all connections asynchronously."""
        if not self.running:
            return
        
        self.running = False
        # Gracefully close all client connections
        for reader, writer in self.client_connections:
            writer.close()
            await writer.wait_closed()
            
        self.client_connections.clear()  # Dọn dẹp danh sách kết nối
        
        # Ensure all active tasks finish before shutting down the server
        await asyncio.sleep(0.1)  # Small delay to let any pending operations complete
        
        self._notify('Server stopped.')  # Thông báo dừng server