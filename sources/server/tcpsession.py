# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import uuid
import typing
import asyncio

from sources.utils import types
from sources.utils.logger import AsyncLogger
from sources.handlers.cmd import CommandHandler
from sources.manager.security import RateLimiter
from sources.server.transport import ClientTransport, PacketHandler



class TcpSession:
    """Manages a TCP session between the server and a client."""

    def __init__(
        self,
        server: types.TcpServer,
        database: typing.Optional[types.SQLite | types.MySQL],
        rate_limiter: RateLimiter,
    ) -> None:
        self.server = server
        self.transport = None
        self.data_handler = None
        self.database = database
        self.is_connected = False
        self.rate_limiter = rate_limiter
        self.reader: typing.Optional[asyncio.StreamReader] = None
        self.writer: typing.Optional[asyncio.StreamWriter] = None
        self.client_address: typing.Optional[typing.Tuple[str, int]] = None

        self.id = uuid.uuid4()
        self.command_handler = CommandHandler(database)

    async def _handle_rate_limit_exceeded(self):
        """Gửi thông báo và ngắt kết nối khi vượt quá giới hạn yêu cầu."""
        await self.data_handler.send({
            "status": False,
            "message": "Too many requests. Please try again in 1 minute."
        })
        await self.disconnect()

    async def connect(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Establish a connection with the client and set session details."""
        try:
            # Lấy thông tin về địa chỉ client
            self.reader = reader
            self.writer = writer
            self.is_connected = True
            self.client_address = writer.get_extra_info('peername')

            if not self.client_address:
                await AsyncLogger.notify_error("Failed to get client address.")
                await self.disconnect()
                return

            # Khởi tạo các lớp transport và data handler
            self.transport = ClientTransport(self.reader, self.writer)
            self.data_handler = PacketHandler(self.transport)

            # Kiểm tra giới hạn tốc độ (rate limiting)
            if not await self.rate_limiter.is_allowed(self.client_address[0]):
                await self._handle_rate_limit_exceeded()
                return

            # Ghi nhật ký khi kết nối thành công
            await AsyncLogger.notify_info(f"Port connected: {self.client_address[1]}")

        except OSError as e:
            await AsyncLogger.notify_error(f"Network error: {e}")
            await self.disconnect()

        except asyncio.IncompleteReadError as e:
            await AsyncLogger.notify_error(f"Incomplete read error: {e}")
            await self.disconnect()

        except Exception as e:
            await AsyncLogger.notify_error(f"Unexpected error during connection: {e}")
            await self.disconnect()

    async def disconnect(self):
        """Safely disconnect the client."""
        if not self.is_connected:
            return

        self.is_connected = False  # Đánh dấu phiên làm việc đã ngắt kết nối

        try:
            # Kiểm tra xem writer có tồn tại và đã được khởi tạo
            if self.writer:
                await self.writer.drain()  # Đảm bảo gửi hết dữ liệu còn lại

                try:
                    await asyncio.wait_for(self.writer.wait_closed(), timeout=2.0)
                except asyncio.TimeoutError:
                    await AsyncLogger.notify_warning(
                        f"Timeout while waiting for writer to close: {self.client_address[1]}"
                    )
                    self.writer.close()  # Đóng writer nếu quá thời gian chờ

            await AsyncLogger.notify_info(f"Port disconnected: {self.client_address[1]}")

        except OSError as e:
            await AsyncLogger.notify_error(f"OSError during disconnection: {e}")

        except asyncio.CancelledError:
            await AsyncLogger.notify_info("Disconnection was cancelled.")

        except Exception as e:
            await AsyncLogger.notify_error(f"Unexpected error during disconnection: {e}")

    async def receive_data(self):
        """Nhận và xử lý dữ liệu từ client với xử lý timeout."""
        while self.is_connected:
            # Nhận dữ liệu từ data_handler
            response = await self.data_handler.receive()

            # Kiểm tra phản hồi nhận được có hợp lệ không
            if response is None:
                await self.disconnect()
                break

            data = response.get("data", None)
            if data is None:
                await self.disconnect()
                break

            code = data.get("code", None)

            if isinstance(code, int):
                # Nhóm các điều kiện ngắt kết nối ngay lập tức
                if code in {404, 1001, 5002, 5003, 5004}:
                    await self.disconnect()
                    break

                # Gửi dữ liệu và ngắt kết nối sau khi gửi
                if code in {2001, 3001, 4001, 4002}:
                    await self.data_handler.send(data)
                    await self.disconnect()
                    break

                # Gửi dữ liệu và tiếp tục nhận (có thể là gửi báo cáo lỗi hoặc xử lý tạm thời)
                if code == 5001:
                    await self.data_handler.send(data)
                    continue

            # Nếu không phải mã lỗi, xử lý lệnh và gửi phản hồi
            response = await self.command_handler.process_command(data)
            await self.data_handler.send(response)