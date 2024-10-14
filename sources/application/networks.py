# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import asyncio
import aiofiles
from typing import Callable, Optional, List, Tuple

from collections import defaultdict
from sources.model.realtime import Realtime
from sources.model.types import AlgorithmTypes
from sources.application.configs import Configs


MAX_CONNECTIONS = 1000  # Define your max connections
BLOCK_TIME = Realtime.timedelta(days=1)  # Time duration for auto-unblocking

MAX_REQUESTS = 10  # Maximum allowed requests in 5 second
REQUEST_WINDOW = 5  # Time window in 5 seconds


class AsyncNetworks(Configs.Network):
    def __init__(
        self, 
        host: str, 
        port: int, 
        algorithm: AlgorithmTypes
    ):
        self.server_address: Tuple[str, int] = (host, port)
        self.algorithm: AlgorithmTypes = algorithm
        self.message_callback: Optional[Callable[[str], None]] = None
        self.running: bool = False  # Initialize with False
        self.client_connections: List[Tuple[asyncio.StreamReader, asyncio.StreamWriter]] = []

        self.block_ips: set = set()  # Set to hold blocked IP addresses
        self.block_ips_lock = asyncio.Lock()
        self.ip_requests = defaultdict(list)  # Track requests per IP (IP: [timestamps])

        asyncio.run(self._load_block_ips())  # Load blocked IPs from file
    
    async def _close_connection(self, writer: asyncio.StreamWriter):
        """Close a client connection."""
        writer.close()
        await writer.wait_closed()  # Đảm bảo writer đã đóng

    def _notify(self, message: str):
        if self.message_callback:
            self.message_callback(f'Notify: {message}')

    def _notify_error(self, message: str):
        if self.message_callback:
            self.message_callback(f'Error: {message}')
    
    async def _save_block_ips(self):
        """Save blocked IP addresses to a file with timestamps."""
        async with self.block_ips_lock:  # Đảm bảo chỉ một task ghi file cùng lúc
            async with aiofiles.open(AsyncNetworks.block_file, mode='w') as file:
                # Ghi mỗi dòng với định dạng: ip_address,timestamp
                for ip in self.block_ips:
                    block_time = self.ip_requests[ip][0].strftime('%Y-%m-%d %H:%M:%S')
                    await file.write(f"{ip},{block_time}\n")
    
    async def _load_block_ips(self):
        """Load blocked IP addresses from a file."""
        try:
            async with aiofiles.open(AsyncNetworks.block_file, mode='r') as file:
                async for line in file:
                    ip, block_time_str = line.strip().split(',')
                    block_time = Realtime.strptime(block_time_str, '%Y-%m-%d %H:%M:%S')
                    self.block_ips.add(ip)
                    self.ip_requests[ip].append(block_time)
        except FileNotFoundError:
            # Nếu file không tồn tại, khởi động với set trống
            self._notify("Blocked IPs file not found. Starting with no blocked IPs.")
    
    async def _track_requests(self, ip_address: str):
        """Track the number of requests from an IP and block if necessary."""
        current_time = Realtime.now()

        # Lọc các request trong khoảng thời gian REQUEST_WINDOW
        self.ip_requests[ip_address] = [
            req_time for req_time in self.ip_requests[ip_address] 
            if (current_time - req_time).total_seconds() < REQUEST_WINDOW
        ]

        # Thêm yêu cầu hiện tại vào danh sách
        self.ip_requests[ip_address].append(current_time)

        # Nếu số lượng yêu cầu quá 10 trong 5 giây, block IP
        if len(self.ip_requests[ip_address]) > 10:
            # Block IP trong bộ nhớ và lưu thời gian block vào ip_requests
            self.block_ips.add(ip_address)
            self.ip_requests[ip_address] = [current_time]  # Lưu thời gian block để dùng cho unblock
            self._notify(f"Blocked IP: {ip_address}")

            # Lưu thông tin block vào file và nạp lại danh sách block
            asyncio.create_task(self._save_block_ips())
            
    def set_message_callback(
        self, callback: Callable[[str], None]
    ):
        self.message_callback = callback
    
    def active_client(self):
        """Return the number of active connections."""
        return len(self.client_connections)
    
    async def auto_unblock_ips(self):
        """Auto unblock IPs after BLOCK_TIME."""
        while self.running:
            current_time = Realtime.now()
            # Unblock IPs that have been blocked for more than BLOCK_TIME
            for ip in list(self.block_ips):  # Create a copy to modify safely
                block_time = self.ip_requests[ip][0]
                if (current_time - block_time).total_seconds() > BLOCK_TIME.total_seconds():
                    self.block_ips.remove(ip)
                    self._notify(f"Unblocked IP: {ip}")
                    asyncio.create_task(self._save_block_ips())

            self._notify_error("Automatically unblock activated IP, run again after 5 minutes.")
            await asyncio.sleep(60 * 5)  # Check every 5 minutes

    async def start(self):
        """Start the server and listen for incoming connections asynchronously."""
        if self.running:
            self._notify_error("Server is already running.")
            return
        
        try:
            self._notify(f'Starting async server at {self.server_address}')
            self.running = True
            
            # Bổ sung SO_REUSEADDR để tránh lỗi cổng bị chiếm dụng
            server = await asyncio.start_server(
                self.handle_client, *self.server_address,
                reuse_address = True  # Cho phép tái sử dụng cổng ngay lập tức
            )

            # Bắt đầu auto unblock IPs
            asyncio.create_task(self.auto_unblock_ips())

            async with server:
                await server.serve_forever()
        except OSError as error:
            self._notify_error(f"OSError: {str(error)} - {self.server_address}")
            await asyncio.sleep(5)  # Retry after 5 seconds
        except Exception as error:
            self._notify_error("Unknown error: " + str(error))

    async def handle_client(
        self, 
        reader: asyncio.StreamReader, 
        writer: asyncio.StreamWriter
    ):
        """Handle data from a client asynchronously with timeout."""
        client_address = writer.get_extra_info('peername')

        if client_address[0] in self.block_ips:
            writer.close()
            await writer.wait_closed()
            return
        
        if len(self.client_connections) >= MAX_CONNECTIONS:
            self._notify_error(f"Connection limit exceeded. Refusing connection from {client_address}")
            writer.close()
            await writer.wait_closed()
            return

        self.client_connections.append((reader, writer))
        if self.DEBUG:self._notify(f"Client connected from {client_address}")

        try:
            while True:
                try:
                    await self._track_requests(client_address[0])

                    # Timeout is set to 60s, adjust as necessary
                    data = await asyncio.wait_for(reader.read(1024), timeout=60.0)  
                except asyncio.TimeoutError:
                    self._notify(f"Client {client_address} timed out.")
                    break
                
                if not data:
                    break  # Client disconnected

                # Handle data from client and send response
                response: bytes = await self.algorithm.handle_data(client_address, data)
                writer.write(response)
                await writer.drain()  # Ensure the data is sent
        except Exception as e:
            self._notify_error(f"Error handling client {client_address}: {e}")
        finally:
            # Ensure client connection is properly closed
            writer.close()
            await writer.wait_closed()
            self.client_connections.remove((reader, writer))
            self._notify(f"Connection with {client_address} closed.")

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
        await self.algorithm.close()  # Đóng thuật toán

        self._notify('Server stopped.')

    