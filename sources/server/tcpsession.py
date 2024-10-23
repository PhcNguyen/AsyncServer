# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import uuid
import typing
import asyncio

from sources.utils import types
from sources.handlers.data import DataHandler
from sources.utils.logger import AsyncLogger
from sources.manager.firewall import RateLimiter
from sources.handlers.command import CommandHandler


class TcpSession:
    """Manages a TCP session between the server and a client."""

    def __init__(
        self,
        server: types.TcpServer,
        database: typing.Optional[types.SQLite | types.MySQL]
    ) -> None:
        self.server = server
        self.database = database
        self.is_connected = False
        self.reader: typing.Optional[asyncio.StreamReader] = None
        self.writer: typing.Optional[asyncio.StreamWriter] = None
        self.client_address: typing.Optional[typing.Tuple[str, int]] = None

        self.id = uuid.uuid4()
        self.data_handler = DataHandler(None)
        self.command_handler = CommandHandler(database)
        self.rate_limiter = RateLimiter(limit=1, period=2)  # Limit 1 request per 2 seconds

    async def connect(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Establish a connection with the client and set session details."""
        try:
            self.client_address = writer.get_extra_info('peername')
            self.reader = reader
            self.writer = writer
            self.is_connected = True

            self.data_handler = DataHandler(self.reader, self.writer)

            # Rate limit check
            if not await self.rate_limiter.is_allowed(self.client_address[0]):
                await self.data_handler.send({
                    "status": False,
                    "message": "Too many requests. Please try again in 1 minute."
                })
                await self.disconnect()
                return

            await AsyncLogger.notify_info(f"Port connected: {self.client_address[1]}")

        except Exception as e:
            await AsyncLogger.notify_error(f"Connection error: {e}")
            await self.disconnect()

    async def disconnect(self):
        """Safely disconnect the client."""
        if not self.is_connected:
            return
        try:
            self.is_connected = False  # Mark the session as disconnected

            # Safely close the writer
            if self.writer:
                await self.writer.drain()
                try:
                    await asyncio.wait_for(self.writer.wait_closed(), timeout=2.0)
                except asyncio.TimeoutError:
                    self.writer.close()

            await AsyncLogger.notify_info(f"Port disconnected: {self.client_address[1]}")

        except Exception as e:
            await AsyncLogger.notify_error(f"Disconnection error: {e}")

    async def receive_data(self):
        """Receive and process data from the client with timeout handling."""
        while self.is_connected:
            data = await self.data_handler.receive()
            code = data.get("code", "")

            if not isinstance(data, dict):
                await AsyncLogger.notify_error("Received data is not a dictionary.")
                await self.disconnect()
                break

            # Handle specific disconnect codes
            if isinstance(code, int) and code in [1001, 3001]:
                await self.disconnect()
                break

            if (isinstance(code, int)
            and code in [404, 5001, 5002, 5003, 5004]
            or not data.get('status')):
                await self.data_handler.send(data)
                await self.disconnect()
                break

            # Process command and send the response
            response = await self.command_handler.process_command(data)
            await self.data_handler.send(response)