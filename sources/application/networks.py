# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import asyncio
from typing import List, Tuple

from client.networks import AsyncClient
from sources.model import types
from sources.application.configs import Configs
from sources.application.firewall import FireWall
from sources.model.logging.serverlogger import AsyncLogger



class AsyncNetworks(Configs.Network):
    MAX_CONNECTIONS = 1000  # Define your max connections

    def __init__(
        self, 
        host: str, 
        port: int, 
        algorithm: types.AlgorithmProcessing
    ):
        self.stop_event = asyncio.Event()
        self.firewall: FireWall = FireWall()
        self.server_address: Tuple[str, int] = (host, port)
        self.algorithm: types.AlgorithmProcessing = algorithm
        self.running: bool = False  # Initialize with False
        self.client_connections: List[Tuple[asyncio.StreamReader, asyncio.StreamWriter]] = []

    @staticmethod
    async def _close_connection(writer: asyncio.StreamWriter):
        """Close a client connection."""
        writer.close()
        await writer.wait_closed()  # Đảm bảo writer đã đóng

    def active_client(self):
        """Return the number of active connections."""
        return len(self.client_connections)

    async def start(self):
        """Start the server and listen for incoming connections asynchronously."""
        if self.running:
            await AsyncLogger.notify("Server is already running.")
            return
        
        try:
            await AsyncLogger.notify(f'Starting async server at {self.server_address}')
            self.running = True
            
            # Bổ sung SO_REUSEADDR để tránh lỗi cổng bị chiếm dụng
            server = await asyncio.start_server(
                self.handle_client, *self.server_address,
                reuse_address = True  # Cho phép tái sử dụng cổng ngay lập tức
            )

            asyncio.create_task(self.firewall.auto_unblock_ips())

            async with server:
                await server.serve_forever()
        except OSError as error:
            await AsyncLogger.notify_error(f"OSError: {str(error)} - {self.server_address}")
            await asyncio.sleep(5)  # Retry after 5 seconds
        except Exception as error:
            await AsyncLogger.notify_error(str(error))

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
        
        if len(self.client_connections) >= AsyncNetworks.MAX_CONNECTIONS:
            await AsyncLogger.notify_error(f"Connection limit exceeded. Refusing connection from {client_address}")
            writer.close()
            await writer.wait_closed()
            return

        self.client_connections.append((reader, writer))
        if self.DEBUG:await AsyncLogger.notify(f"Client connected from {client_address}")

        try:
            while True:
                try:
                    await self.firewall.track_requests(client_address[0])

                    # Timeout is set to 60s, adjust as necessary
                    data = await asyncio.wait_for(reader.read(1024), timeout=60.0)  
                except asyncio.TimeoutError:
                    if self.DEBUG:await AsyncLogger.notify(f"Client {client_address} timed out.")
                    break
                
                if not data:
                    break  # Client disconnected

                # Handle data from client and send response
                response: bytes = await self.algorithm.handle_data(client_address, data)
                writer.write(response)
                await writer.drain()  # Ensure the data is sent
        except Exception as e:
            await AsyncLogger.notify_error(f"{client_address}: {e}")
        finally:
            # Ensure client connection is properly closed
            writer.close()
            await writer.wait_closed()
            self.client_connections.remove((reader, writer))
            if self.DEBUG:await AsyncLogger.notify(f"Connection with {client_address} closed.")

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

        await AsyncLogger.notify('Server stopped.')