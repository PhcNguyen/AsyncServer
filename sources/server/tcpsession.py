# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import uuid
import asyncio

from sources.model import types
from sources.handler.data import DataHandler
from sources.model.logging import AsyncLogger
from sources.manager.firewall import RateLimiter
from sources.handler.command import CommandHandler



class TcpSession:
    def __init__(self, server: types.TcpServer, sql: types.DatabaseManager):
        self.sqlite = sql
        self.server = server
        self.client_ip = None
        self.client_port = None
        self.is_connected = False  # Thêm thuộc tính này để theo dõi trạng thái kết nối

        self.id = uuid.uuid4()

        self.rate_limiter = RateLimiter(limit=5, period=10)  # 5 yêu cầu trong 10 giây
        self.connection_manager = ConnectionManager(server)
        self.data_handler = DataHandler(None)
        self.command_handler = CommandHandler(sql)

    async def receive_data(self):
        while self.is_connected:
            try:
                if not await self.rate_limiter.is_allowed(self.client_ip):
                    response = {"status": False, "message": "Too many requests. Please try again in 10 minutes."}
                    await self.data_handler.send(response)
                    await self.disconnect()  # Ngắt kết nối
                    break

                data = await self.data_handler.receive()
                if data:
                    response =await self.command_handler.handle_command(data)
                    await self.data_handler.send(response)
                else:
                    # Nếu không nhận được dữ liệu, coi như kết nối đã bị ngắt
                    await AsyncLogger.notify("No data received, disconnecting...")
                    await self.disconnect()  # Ngắt kết nối
                    break  # Thoát khỏi vòng lặp
            except asyncio.CancelledError:
                await AsyncLogger.notify("Receive task was cancelled.")  # Log khi task bị hủy
                break  # Dừng vòng lặp nếu task bị hủy
            except Exception as e:
                await AsyncLogger.notify_error(f"Error during receive_data: {e}")  # Log lỗi khi có ngoại lệ
                error_message = {
                    "status": False,
                    "message": f"Error during receive: {str(e)}"
                }
                await self.data_handler.send(error_message)  # Giả sử data_handler có hàm send
                await self.disconnect()  # Ngắt kết nối khi có lỗi

    async def connect(self, reader, writer):
        # Thiết lập transport
        self.client_ip = writer.get_extra_info('peername')[0]
        self.connection_manager.transport = writer
        await self.connection_manager.connect()

        # Gán transport cho DataHandler
        self.data_handler = DataHandler(reader)
        self.is_connected = True

        await AsyncLogger.notify(
            f"Connected: {self.id} to {writer.get_extra_info('peername')}")  # Log khi kết nối thành công

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