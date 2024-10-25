# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import asyncio
from typing import List, Tuple

from sources.utils import types
from sources.utils.logger import AsyncLogger
from sources.server.tcpsession import TcpSession
from sources.manager.security import RateLimiter
from sources.utils.system import InternetProtocol



class TcpServer:
    DEBUG: bool = False
    PORT: int   = 7272                       # Default port number
    LOCAL: str  = InternetProtocol.local()   # Retrieve local IP address
    PUBLIC: str = InternetProtocol.public()  # Retrieve public IP address
    MAX_CONNECTIONS = 1000000                # Giới hạn số lượng kết nối tối đa

    def __init__(
        self, host: str, port: int,
        database: types.SQLite | types.MySQL
    ) -> None:
        self.host = host
        self.port = port
        self.running = False
        self.database = database
        self.current_connections = 0

        self.stop_event = asyncio.Event()
        self.rate_limiter = RateLimiter(limit=3, period=1)  # Limit 3 request per 1 seconds
        self.server_address: Tuple[str, int] = (host, port)
        self.client_handler = ClientHandler(self, self.database, self.rate_limiter)

    async def start(self):
        """Start the server and listen for incoming connections asynchronously."""
        if self.running:
            await AsyncLogger.notify_info("Server is already running")
            return

        if not await self.database.start():
            self.running = False
            await AsyncLogger.notify_info("SQL error occurred")
            return

        await asyncio.sleep(2)

        try:
            self.running = True
            self.rate_limiter.running = True
            await AsyncLogger.notify_info(f'Server processing Commands run at {self.server_address}')

            server = await asyncio.start_server(
                self.client_handler.handle_client,
                *self.server_address, reuse_address=True
            )

            asyncio.create_task(self.rate_limiter.clean_inactive_ips())

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
            await AsyncLogger.notify_info("The server has stopped")
            return

        self.running = False
        self.rate_limiter.running = False

        await self.client_handler.close_all_connections()
        await self.database.close()

        await AsyncLogger.notify_info('The server has stopped')



class ClientHandler:
    def __init__(self,
        server: TcpServer,
        database: types.SQLite | types.MySQL,
        rate_limiter: RateLimiter
    ) -> None:
        self.server = server
        self.database = database
        self.rate_limiter = rate_limiter
        self.client_connections: List[TcpSession] = []  # Store TcpSession objects

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle data from a client asynchronously with timeout."""

        # Create TcpSession for the connected client
        session = TcpSession(self.server, self.database, self.rate_limiter)
        await session.connect(reader, writer)

        self.client_connections.append(session)
        self.server.current_connections += 1  # Tăng số lượng kết nối

        try:
            # Wait for the client to send data or for the connection to be closed
            await session.receive_data()  # This will manage waiting for data.
        finally:
            await self.close_connection(session)

    async def close_connection(self, session: TcpSession):
        """Close a client connection."""
        try:
            # Ensure the session is connected before trying to disconnect
            if session.is_connected:
                await session.disconnect()    # Close the session properly
                session.is_connected = False  # Mark the session as disconnected

                # Remove the session only if it's still in the list
                if session in self.client_connections:
                    self.client_connections.remove(session)

            self.server.current_connections -= 1
        except Exception as e:
            # Catch any unexpected errors during disconnection
            await AsyncLogger.notify_error(f"Error while closing connection: {e}")

    async def close_all_connections(self):
        """Close all client connections."""
        if not self.client_connections:
            await AsyncLogger.notify_info("No connections to close.")
            return

        # Create a list to hold the tasks
        close_tasks = []

        # Schedule each close_connection call as a task
        for session in self.client_connections:
            task = asyncio.create_task(self.close_connection(session))
            close_tasks.append(task)

        # Optionally await each task if you need to ensure they complete later
        for task in close_tasks:
            await task

        self.client_connections.clear()  # Clear the list of connections
        await AsyncLogger.notify_info("All connections closed successfully.")