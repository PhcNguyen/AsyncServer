# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import asyncio
from typing import List, Tuple

from sources.utils import types
from sources.utils.logger import Logger
from sources.server.tcpsession import TCPSession
from sources.manager.security import RateLimiter
from sources.utils.system import InternetProtocol
from sources.server.tcpcontroller import TCPController


class TCPServer:
    DEBUG: bool = False
    PORT: int = 7272  # Default port number
    LOCAL: str = InternetProtocol.local()  # Retrieve local IP address
    PUBLIC: str = InternetProtocol.public()  # Retrieve public IP address
    MAX_CONNECTIONS = 1000000  # Giới hạn số lượng kết nối tối đa

    def __init__(self, host: str, port: int, database: types.SQLite | types.MySQL) -> None:
        self.host = host
        self.port = port
        self.running = False
        self.database = database
        self.current_connections = 0

        self.stop_event = asyncio.Event()
        self.rate_limiter = RateLimiter(limit=3, period=1)  # Limit 3 requests per 1 second
        self.server_address: Tuple[str, int] = (host, port)
        self.client_handler = ClientHandler(self, self.database, self.rate_limiter)

    async def start(self):
        """Start the server and listen for incoming connections asynchronously."""
        if self.running:
            await Logger.info("Server is already running")
            return

        if not await self.database.start():
            self.running = False
            await Logger.info("SQL error occurred")
            return

        await asyncio.sleep(2)

        try:
            self.running = True
            self.rate_limiter.running = True
            await Logger.info(f'Server processing Commands run at {self.server_address}')

            server = await asyncio.start_server(
                self.client_handler.handle_client,
                *self.server_address, reuse_address=True
            )

            asyncio.create_task(self.rate_limiter.clean_inactive_ips())

            async with server:
                await server.serve_forever()

        except OSError as error:
            self.running = False
            await Logger.error(f"OSError: {str(error)} - {self.server_address}")
            await asyncio.sleep(5)  # Retry after 5 seconds

        except Exception as error:
            self.running = False
            await Logger.error(f"Server: {error}")

    async def stop(self):
        """Stop the server asynchronously."""
        if not self.running:
            await Logger.info("The server has stopped")
            return

        self.running = False
        self.rate_limiter.running = False

        await self.client_handler.close_all_connections()
        await self.database.close()

        await Logger.info('The server has stopped')


class ClientHandler:
    def __init__(self, server: TCPServer, database: types.SQLite | types.MySQL, rate_limiter: RateLimiter):
        self.server = server
        self.database = database
        self.rate_limiter = rate_limiter
        self.client_connections: List[TCPSession] = []  # Store TCPSession objects

    async def check_rate_limit(self, session: TCPSession) -> bool:
        """Check if the client's request rate is within allowed limits."""
        if not await self.rate_limiter.is_allowed(session.client_address[0]):
            await Logger.warning("Rate limit exceeded. Disconnecting client.")
            await session.disconnect()  # Disconnect the session if rate limit is exceeded
            return False  # Indicate that the rate limit check failed
        return True  # Indicate that the rate limit check passed

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle data from a client asynchronously with timeout."""
        session = TCPSession()
        await session.connect(reader, writer)

        if not await self.check_rate_limit(session):
            return  # Terminate if rate limit is exceeded

        # Initialize the TCP controller with the database and transport
        controller = TCPController(self.database, session.transport)

        self.client_connections.append(session)
        self.server.current_connections += 1  # Increase the number of connections

        try:
            while session.is_connected:
                try:
                    code, command, data = await session.transport.receive()  # Receive data from the client
                except Exception as e:
                    await Logger.error(f"Error receiving data: {e}")
                    break  # Break out of the loop on error

                code = await controller.handle_command(code, command, data)  # Use the controller to handle the command

                if code == 1:
                    continue  # Continue if code is 1
                elif code == 0:
                    await session.disconnect()
                    break  # Disconnect if code is 0
        finally:
            await self.close_connection(session)  # Ensure connection is closed

    async def close_connection(self, session: TCPSession):
        """Close a client connection."""
        try:
            if session.is_connected:
                await session.disconnect()  # Close the session properly
                session.is_connected = False  # Mark the session as disconnected

                if session in self.client_connections:
                    self.client_connections.remove(session)

                self.server.current_connections -= 1  # Decrease the current connection count
        except Exception as e:
            await Logger.error(f"Error while closing connection: {e}")

    async def close_all_connections(self):
        """Close all client connections."""
        if not self.client_connections:
            await Logger.info("No connections to close.")
            return

        close_tasks = [asyncio.create_task(self.close_connection(session)) for session in self.client_connections]

        for task in close_tasks:
            await task

        self.client_connections.clear()  # Clear the list of connections
        await Logger.info("All connections closed successfully.")