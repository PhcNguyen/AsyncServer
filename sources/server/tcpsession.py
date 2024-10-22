# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import uuid
import asyncio

from typing import Optional, Tuple
from sources.utils import types
from sources.server.data import DataHandler
from sources.utils.logger import AsyncLogger
from sources.manager.firewall import RateLimiter
from sources.handlers.command import CommandHandler



class TcpSession:
    def __init__(self,
        server: types.TcpServer,
        database: Optional[types.SQLite | types.MySQL]
    ) -> None:
        self.database = database
        self.server = server
        self.client_address: Optional[Tuple[str, int]] = None
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self.is_connected = False
        self.id = uuid.uuid4()

        self.rate_limiter = RateLimiter(limit=5, period=5)  # Giới hạn 5 yêu cầu trong 5 giây
        self.data_handler = DataHandler(None)
        self.command_handler = CommandHandler(database)

    async def connect(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Kết nối với client và thiết lập thông tin phiên."""
        try:
            self.client_address = writer.get_extra_info('peername')

            self.reader = reader
            self.writer = writer
            self.is_connected = True

            self.data_handler = DataHandler(self.reader, self.writer)

            # Kiểm tra giới hạn tốc độ
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
        """Ngắt kết nối client một cách an toàn."""
        #if not self.is_connected: return
        print(self.is_connected)
        try:
            # Đánh dấu phiên làm việc đã bị ngắt
            self.is_connected = False
            # Đóng writer nếu tồn tại
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
        """Nhận dữ liệu từ client với timeout."""
        while self.is_connected:
            try:
                data = await self.data_handler.receive()
                code = data.get("code")

                if not isinstance(data, dict):
                    await AsyncLogger.notify_error("Received data is not a dictionary.")
                    await self.disconnect()
                    break

                # Ngắt kết nối nếu có lỗi hoặc status False
                if isinstance(code, int) and code == 404:
                    await self.disconnect()
                    break

                if (isinstance(code, int)
                and code in [5001, 5002, 3001, 4002]
                or not data.get('status')):
                    await self.data_handler.send(data)
                    await self.disconnect()
                    break

                response = await self.command_handler.process_command(data)
                await self.data_handler.send(response)

            except Exception as e:
                # Log lỗi nếu xảy ra, sau đó ngắt kết nối
                await AsyncLogger.notify_error(f"Error during receive_data: {e}")
                await self.disconnect()
                break