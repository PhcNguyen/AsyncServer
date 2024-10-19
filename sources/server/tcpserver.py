# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import asyncio
from typing import List, Tuple

from sources import configs
from sources.utils import types
from sources.utils.logger import AsyncLogger
from sources.manager.firewall import IPFirewall
from sources.server.tcpsession import TcpSession




class TcpServer(configs.NetworkConfigs):
    MAX_CONNECTIONS = 1000000  # Giới hạn số lượng kết nối tối đa

    def __init__(self, host: str, port: int, sql: types.DatabaseManager):
        self.stop_event = asyncio.Event()
        self.firewall = IPFirewall()
        self.server_address: Tuple[str, int] = (host, port)
        self.running: bool = False
        self.client_handler = ClientHandler(self, self.firewall, sql)
        self.current_connections = 0  # Số lượng kết nối hiện tại

    async def start(self):
        """Start the server and listen for incoming connections asynchronously."""
        if self.running:
            await AsyncLogger.notify("Server is already running.")
            return

        try:
            await AsyncLogger.notify(f'Server processing Commands run at {self.server_address}')
            self.running = True

            server = await asyncio.start_server(
                self.client_handler.handle_client, *self.server_address,
                reuse_address=True
            )

            # asyncio.create_task(self.firewall.auto_unblock_ips())

            async with server:
                await server.serve_forever()
        except OSError as error:
            await AsyncLogger.notify_error(f"OSError: {str(error)} - {self.server_address}")
            await asyncio.sleep(5)  # Retry after 5 seconds
        except Exception as error:
            await AsyncLogger.notify_error(str(error))

    async def stop(self):
        """Stop the server asynchronously."""
        if not self.running:
            return

        self.running = False
        await self.client_handler.close_all_connections()
        await AsyncLogger.notify('Server stopped.')

    def increment_connection(self):
        self.current_connections += 1

    def decrement_connection(self):
        self.current_connections -= 1

    def can_accept_connections(self):
        return self.current_connections < self.MAX_CONNECTIONS



class ClientHandler:
    def __init__(self, tcp_server: TcpServer, firewall: IPFirewall, sql: types.DatabaseManager):
        self.sql = sql
        self.firewall = firewall
        self.tcp_server = tcp_server
        self.client_connections: List[TcpSession] = []  # Store TcpSession objects

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle data from a client asynchronously with timeout."""
        client_address = writer.get_extra_info('peername')

        if client_address[0] in self.firewall.block_ips:
            writer.write(self.firewall.remaining_time(client_address[0]))
            await writer.drain()  # Đảm bảo dữ liệu được gửi đi

            writer.close()
            await writer.wait_closed()
            return

        # Create TcpSession for the connected client
        session = TcpSession(self.tcp_server, self.sql)
        await session.connect(reader, writer)
        self.client_connections.append(session)
        self.tcp_server.increment_connection()  # Tăng số lượng kết nối

        try:
            while session.is_connected:
                await asyncio.sleep(1)  # Keep the session alive
        finally:
            await self.close_connection(session)

    async def close_connection(self, session: TcpSession):
        """Close a client connection."""
        await session.disconnect()  # Close the session properly
        self.client_connections.remove(session)
        self.tcp_server.decrement_connection()  # Giảm số lượng kết nối

    async def close_all_connections(self):
        """Close all client connections."""
        close_tasks = [self.close_connection(session) for session in self.client_connections]
        await asyncio.gather(*close_tasks)
        self.client_connections.clear()