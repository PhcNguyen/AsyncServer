# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import uuid
import typing
import asyncio

from sources.utils.logger import Logger
from sources.server.IO.transport import Transport


class TCPSession:
    """Manages a TCP session between the server and a client."""

    def __init__(self) -> None:
        self.transport = None
        self.controller = None
        self.data_handler = None
        self.is_connected = False
        self.reader: typing.Optional[asyncio.StreamReader] = None
        self.writer: typing.Optional[asyncio.StreamWriter] = None
        self.client_address: typing.Optional[typing.Tuple[str, int]] = None
        self.id = uuid.uuid4()  # Unique identifier for the session

    async def connect(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Establish a connection with the client and set session details."""
        try:
            # Get the client address information
            self.reader = reader
            self.writer = writer
            self.is_connected = True
            self.transport = Transport(self.reader, self.writer)
            self.client_address = writer.get_extra_info('peername')

            if not self.client_address:
                await Logger.error("Failed to get client address.")
                await self.disconnect()
                return

            # Log successful connection
            await Logger.info(f"Accepted Session: {self.id} Successful")

        except OSError as error:
            await Logger.error(f"Network error: {error}")
            await self.disconnect()

        except asyncio.IncompleteReadError as error:
            await Logger.error(f"Incomplete read error: {error}")
            await self.disconnect()

        except Exception as error:
            await Logger.error(f"Unexpected error during connection: {error}")
            await self.disconnect()

    async def disconnect(self):
        """Safely disconnect the client."""
        if not self.is_connected:
            return

        self.is_connected = False  # Mark the session as disconnected

        try:
            # Check if writer exists and has been initialized
            if self.writer:
                await self.writer.drain()  # Ensure all remaining data is sent

                try:
                    await asyncio.wait_for(self.writer.wait_closed(), timeout=2.0)
                except asyncio.TimeoutError:
                    await Logger.warning(f"Timeout while waiting for writer to close: {self.id}")
                    self.writer.close()  # Close writer if timeout occurs

            await Logger.info(f"Session: {self.id} disconnected...")

        except OSError as error:
            await Logger.error(f"OSError during disconnection: {error}")

        except asyncio.CancelledError:
            await Logger.info("Disconnection was cancelled.")

        except Exception as error:
            await Logger.error(f"Unexpected error during disconnection: {error}")