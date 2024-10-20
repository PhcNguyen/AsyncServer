# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import asyncio
from typing import List, Tuple

from sources.utils import types, system
from sources.utils.logger import AsyncLogger
from sources.server.tcpsession import TcpSession



class TcpServer:
    """
        Configuration settings for network communication.

        Attributes:
        - LOCAL (str): Local IP address of the machine.
        - PUBLIC (str): Public IP address of the machine.
        - PORT (int): Port number for network communication (default is 7272).

    """
    DEBUG: bool = False
    PORT: int = 7272  # Default port number
    LOCAL: str = system.InternetProtocol.local()  # Retrieve local IP address
    PUBLIC: str = system.InternetProtocol.public()  # Retrieve public IP address
    MAX_CONNECTIONS = 1000000  # Giới hạn số lượng kết nối tối đa


    def __init__(self, host: str, port: int, sql: types.SQLite | types.MySQL):
        self.sql = sql
        self.host = host
        self.port = port

        self.stop_event = asyncio.Event()
        self.server_address: Tuple[str, int] = (host, port)
        self.running: bool = False
        self.client_handler = ClientHandler(self, self.sql)
        self.current_connections = 0  # Số lượng kết nối hiện tại

    async def start(self):
        """Start the server and listen for incoming connections asynchronously."""
        if self.running:
            await AsyncLogger.notify("Server is already running")
            return

        if not await self.sql.start():
            self.running = False
            await AsyncLogger.notify("SQL error occurred")
            return

        await asyncio.sleep(2)

        try:
            self.running = True
            await AsyncLogger.notify(f'Server processing Commands run at {self.server_address}')

            server = await asyncio.start_server(
                self.client_handler.handle_client, *self.server_address,
                reuse_address=True
            )

            # asyncio.create_task(self.firewall.auto_unblock_ips())

            async with server:
                await server.serve_forever()
        except OSError as error:
            self.running = False
            await AsyncLogger.notify_error(f"OSError: {str(error)} - {self.server_address}")
            await asyncio.sleep(5)  # Retry after 5 seconds
        except Exception as error:
            self.running = False
            await AsyncLogger.notify_error(f"Server: {error}")

    async def stop(self):
        """Stop the server asynchronously."""
        if not self.running:
            await AsyncLogger.notify("The server has stopped")
            return

        self.running = False

        await self.sql.close()
        await self.client_handler.close_all_connections()
        await AsyncLogger.notify('The server has stopped')

    def increment_connection(self):
        self.current_connections += 1

    def decrement_connection(self):
        self.current_connections -= 1

    def can_accept_connections(self):
        return self.current_connections < self.MAX_CONNECTIONS



class ClientHandler:
    def __init__(self, tcp_server: TcpServer, sql: types.SQLite | types.MySQL):
        self.sql = sql
        self.tcp_server = tcp_server
        self.client_connections: List[TcpSession] = []  # Store TcpSession objects

        asyncio.create_task(self.check_disconnected_clients())

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle data from a client asynchronously with timeout."""
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

    async def check_disconnected_clients(self):
        """Periodically check and close disconnected client sessions."""
        while True:
            await asyncio.sleep(5)  # Check every 5 seconds (adjust if needed)

            disconnected_sessions = [
                session for session in self.client_connections
                if not session.is_connected
            ]

            for session in disconnected_sessions:
                await self.close_connection(session)

    async def close_connection(self, session: TcpSession):
        """Close a client connection."""
        try:
            # Ensure the session is connected before trying to disconnect
            if session.is_connected:
                await session.disconnect()  # Close the session properly
                session.is_connected = False  # Mark the session as disconnected

                # Remove the session only if it's still in the list
                if session in self.client_connections:
                    self.client_connections.remove(session)
                else:
                    await AsyncLogger.notify(f"Session {session.id} already removed from the list.")

                # Decrement the connection count
                self.tcp_server.decrement_connection()
            else:
                await AsyncLogger.notify(f"Session {session.id} already disconnected.")
        except Exception as e:
            # Catch any unexpected errors during disconnection
            await AsyncLogger.notify_error(f"Error while closing connection: {e}")

    async def close_all_connections(self):
        """Close all client connections."""
        close_tasks = [self.close_connection(session) for session in self.client_connections]
        await asyncio.gather(*close_tasks)
        self.client_connections.clear()