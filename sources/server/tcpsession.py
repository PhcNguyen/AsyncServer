# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import uuid
import json
import asyncio

from sources.utils import types
from sources.handlers.client.data import DataHandler
from sources.utils.logger import AsyncLogger
from sources.manager.firewall import RateLimiter
from sources.handlers.client.command import CommandHandler



class TcpSession:
    def __init__(self, server: types.TcpServer, sql: types.SQLite | types.MySQL):
        self.sqlite = sql
        self.server = server
        self.client_ip = None
        self.client_port = None
        self.is_connected = False

        self.id = uuid.uuid4()
        self.rate_limiter = RateLimiter(limit=5, period=5)  # 5 requests in 5 seconds
        self.connection_manager = ConnectionManager(server)
        self.data_handler = DataHandler(None)
        self.command_handler = CommandHandler(sql)

    async def receive_data(self):
        while self.is_connected:
            try:
                data = await self.data_handler.receive()  # Receive the decoded data
                if data:
                    # Process the data
                    response = await self.command_handler.handle_command(data)  # Process with command handler
                    await self.data_handler.send(response)  # Send the response back to the client
                else:
                    # No data received, disconnect
                    await self.disconnect()  # Disconnect if no data is received
                    break

            except asyncio.CancelledError:
                await AsyncLogger.notify("Receive task was cancelled.")  # Log if task is cancelled
                break
            except Exception as e:
                await AsyncLogger.notify_error(f"Error during receive_data: {e}")
                # Send error response to client
                await self.data_handler.send({"status": False, "message": str(e)})
                await self.disconnect()  # Disconnect on error
                break

    async def connect(self, reader, writer):
        client_address = writer.get_extra_info('peername')
        self.client_ip, self.client_port = client_address

        self.connection_manager.transport = writer
        await self.connection_manager.connect()

        self.data_handler = DataHandler(reader, writer)
        self.is_connected = True

        if not await self.rate_limiter.is_allowed(self.client_ip):
            response = {"status": False, "message": "Too many requests. Please try again in 1 minute."}
            writer.write(json.dumps(response).encode('utf-8'))
            await writer.drain()
            writer.close()
            await writer.wait_closed()
            return

        await AsyncLogger.notify(f"Port connected: {self.client_port}")
        asyncio.create_task(self.receive_data())

    async def disconnect(self):
        if self.is_connected:  # Kiểm tra trạng thái kết nối trước khi ngắt kết nối
            self.is_connected = False
            await self.connection_manager.disconnect()


class ConnectionManager:
    def __init__(self, server, transport=None):
        self.server = server
        self.transport = transport
        self.is_connected = False

    async def connect(self):
        self.is_connected = True
        # await AsyncLogger.notify(f"Connected session on {self.server}.")

    async def disconnect(self):
        if self.is_connected:
            self.is_connected = False
            # await AsyncLogger.notify(f"Disconnected session from {self.server}.")
            if self.transport:
                self.transport.close()