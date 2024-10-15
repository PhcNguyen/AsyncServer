# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import asyncio
from typing import Callable, Optional, List, Tuple, Any

from sources.model import types
from sources.application.configs import Configs
from sources.application.firewall import FireWall

MAX_CONNECTIONS = 1000  # Define your max connections


class AsyncNetworks(Configs.Network):
    def __init__(
        self, 
        host: str, 
        port: int, 
        algorithm: types.AlgorithmProcessing
    ):
        # Notification lists
        self.notify: List[str] = []
        self.notify_error: List[str] = []

        self.stop_event = asyncio.Event()
        self.server_address: Tuple[str, int] = (host, port)
        self.algorithm: types.AlgorithmProcessing = algorithm
        self.message_callback: Optional[Callable[[str], None]] = None
        self.running: bool = False  # Initialize with False
        self.client_connections: List[Tuple[asyncio.StreamReader, asyncio.StreamWriter]] = []

        self.firewall = FireWall()

    @staticmethod
    async def _close_connection(writer: asyncio.StreamWriter):
        """Close a client connection."""
        writer.close()
        await writer.wait_closed()  # Đảm bảo writer đã đóng

    async def _auto_notify(self):
        # Chuyển thông báo từ firewall vào notify và notify_error
        while not self.stop_event.is_set():
            if not self.message_callback: break

            while self.firewall.notify:
                # Lấy và xóa thông báo đầu tiên từ firewall.notify
                self.notify.append(self.firewall.notify.pop(0))

            while self.firewall.notify_error:
                self.notify_error.append(self.firewall.notify_error.pop(0))

            while self.notify:  # Kiểm tra nếu có thông báo trong notify
                message = self.notify.pop(0)  # Lấy và xóa thông báo đầu tiên
                if message is not None:
                    self.message_callback(f'Notify: {message}')  # Gửi thông báo

            while self.notify_error:  # Kiểm tra nếu có thông báo trong notify_error
                message = self.notify_error.pop(0)  # Lấy và xóa thông báo đầu tiên
                if message is not None:
                    self.message_callback(f'Error: {message}')  # Gửi thông báo

            await asyncio.sleep(0.2)
            
    def set_message_callback(
        self, callback: Callable[[str], None]
    ):
        self.message_callback = callback

    
    def active_client(self):
        """Return the number of active connections."""
        return len(self.client_connections)

    async def start(self):
        """Start the server and listen for incoming connections asynchronously."""
        if self.running:
            self.notify.append("Server is already running.")
            return
        
        try:
            self.notify.append(f'Starting async server at {self.server_address}')
            self.running = True
            
            # Bổ sung SO_REUSEADDR để tránh lỗi cổng bị chiếm dụng
            server = await asyncio.start_server(
                self.handle_client, *self.server_address,
                reuse_address = True  # Cho phép tái sử dụng cổng ngay lập tức
            )

            asyncio.create_task(self._auto_notify())
            asyncio.create_task(self.firewall.auto_unblock_ips())

            async with server:
                await server.serve_forever()
        except OSError as error:
            self.notify_error.append(f"OSError: {str(error)} - {self.server_address}")
            await asyncio.sleep(5)  # Retry after 5 seconds
        except Exception as error:
            self.notify_error.append(str(error))

    async def handle_client(
        self, 
        reader: asyncio.StreamReader, 
        writer: asyncio.StreamWriter
    ):
        """Handle data from a client asynchronously with timeout."""
        client_address = writer.get_extra_info('peername')

        if client_address[0] in self.firewall.block_ips:
            writer.close()
            await writer.wait_closed()
            return
        
        if len(self.client_connections) >= MAX_CONNECTIONS:
            self.notify_error.append(f"Connection limit exceeded. Refusing connection from {client_address}")
            writer.close()
            await writer.wait_closed()
            return

        self.client_connections.append((reader, writer))
        if self.DEBUG:self.notify.append(f"Client connected from {client_address}")

        try:
            while True:
                try:
                    await self.firewall.track_requests(client_address[0])

                    # Timeout is set to 60s, adjust as necessary
                    data = await asyncio.wait_for(reader.read(1024), timeout=60.0)  
                except asyncio.TimeoutError:
                    if self.DEBUG:self.notify.append(f"Client {client_address} timed out.")
                    break
                
                if not data:
                    break  # Client disconnected

                # Handle data from client and send response
                response: bytes = await self.algorithm.handle_data(client_address, data)
                writer.write(response)
                await writer.drain()  # Ensure the data is sent
        except Exception as e:
            self.notify_error.append(f"{client_address}: {e}")
        finally:
            # Ensure client connection is properly closed
            writer.close()
            await writer.wait_closed()
            self.client_connections.remove((reader, writer))
            self.notify.append(f"Connection with {client_address} closed.")

    async def stop(self):
        """Stop the server and close all connections asynchronously."""
        if not self.running:
            return
        
        self.running = False

        # Tạo danh sách các tác vụ đóng kết nối
        close_tasks = []
        for reader, writer in self.client_connections:
            close_tasks.append(self._close_connection(writer))
        
        # Chờ tất cả các tác vụ đóng kết nối hoàn thành
        await asyncio.gather(*close_tasks)

        self.client_connections.clear()

        await self.algorithm.close()
        await self.firewall.close()

        self.notify.append('Server stopped.')