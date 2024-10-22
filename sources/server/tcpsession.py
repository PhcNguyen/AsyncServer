# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import uuid
import json
import asyncio

from sources.utils import types
from sources.server.data import DataHandler
from sources.utils.logger import AsyncLogger
from sources.manager.firewall import RateLimiter
from sources.handlers.command import CommandHandler



class TcpSession:
    def __init__(self, server: types.TcpServer, sql: types.SQLite | types.MySQL):
        self.sqlite = sql
        self.server = server
        self.transport = None
        self.client_ip = None
        self.client_port = None
        self.is_connected = False

        self.id = uuid.uuid4()
        self.rate_limiter = RateLimiter(limit=5, period=5)  # 5 requests in 5 seconds
        self.data_handler = DataHandler(None)
        self.command_handler = CommandHandler(sql)

    async def connect(self, reader, writer):
        client_address = writer.get_extra_info('peername')
        self.client_ip, self.client_port = client_address

        self.transport = writer  # Store the transport
        self.is_connected = True

        self.data_handler = DataHandler(reader, self.transport)

        if not await self.rate_limiter.is_allowed(self.client_ip):
            response = {"status": False, "message": "Too many requests. Please try again in 1 minute."}
            writer.write(json.dumps(response).encode('utf-8'))
            await writer.drain()
            writer.close()
            await writer.wait_closed()
            return

        await AsyncLogger.notify(f"Port connected: {self.client_port}")

    async def disconnect(self):
        if self.is_connected:  # Ensure connection status before disconnecting
            self.is_connected = False
            if self.transport:  # Close the transport if it exists
                self.transport.close()
                await self.transport.wait_closed()
            await AsyncLogger.notify(f"Port disconnected: {self.client_port}")

    async def receive_data(self):
        """Receive data from the client."""
        while self.is_connected:
            try:
                # Wait for data with a 60-second timeout
                data = await asyncio.wait_for(self.data_handler.receive(), timeout=60.0)

                if data.get('error_code') in [5001, 5002]:
                    await self.disconnect()
                    break

                if data.get('status') is False:  # Check if the response indicates an error
                    await self.disconnect()
                    break

                # Process the received data here
                response = await self.command_handler.process_command(data)  # Process with command handler
                await self.data_handler.send(response)  # Send the response back to the client

            except asyncio.TimeoutError:
                # await AsyncLogger.notify(f"Timeout occurred for session {self.id}. Disconnecting.")
                await self.disconnect()  # Disconnect the session on timeout
                break  # Exit the loop on timeout

            except Exception as e:
                await AsyncLogger.notify_error(f"Error during receive_data: {e}")
                await self.disconnect()  # Disconnect on error
                break