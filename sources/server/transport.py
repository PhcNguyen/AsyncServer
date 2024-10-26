# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import json
import asyncio

from typing import Optional, Union
from sources.utils.logger import Logger
from sources.utils.result import ResultBuilder

logger = Logger("transport.log")

async def log_error(message: str, error_code: int) -> dict:
    """Hàm trợ giúp để ghi lỗi và trả về phản hồi lỗi."""
    await logger.log(message, level="ERROR")
    return ResultBuilder.error(error_code)



class ClientTransport:
    """Quản lý việc truyền dữ liệu qua các luồng bất đồng bộ."""

    BUFFER_SIZE = 8192  # Kích thước bộ đệm

    def __init__(self, reader: asyncio.StreamReader = None, writer: asyncio.StreamWriter = None) -> None:
        self.reader = reader
        self.writer = writer
        self.bytes_sent = 0
        self.send_buffer = bytearray()

    async def send_data(self) -> Optional[dict]:
        """Gửi dữ liệu từ bộ đệm một cách bất đồng bộ."""
        if not self.writer:
            return await log_error("Writer không khả dụng.", 1001)

        try:
            while self.send_buffer:
                # Send the data in chunks
                bytes_to_send = len(self.send_buffer)
                self.writer.write(self.send_buffer)  # Write to the stream
                await self.writer.drain()  # Ensure the data is flushed

                await logger.log(f"Đã gửi {bytes_to_send} bytes.")
                self.bytes_sent += bytes_to_send  # Track total bytes sent
                self.send_buffer.clear()  # Clear the buffer after sending

            return ResultBuilder.success(9501, bytes_sent=self.bytes_sent)

        except OSError as error:
            error_code = 5002 if error.errno == 64 else 5003
            return await log_error(f"Lỗi OSError: {error}", error_code)

        except Exception as error:
            return await log_error(f"Lỗi khi gửi: {error}", 5004)

    async def receive_data(self) -> Optional[dict]:
        """Nhận và trả về dữ liệu từ luồng."""
        if not self.reader:
            return await log_error("Reader không khả dụng.", 1001)

        try:
            data = await asyncio.wait_for(self.reader.read(self.BUFFER_SIZE), timeout=120.0)
            if data.strip():
                return ResultBuilder.success(9502, data=data)
            
            return None

        except asyncio.TimeoutError:
            return await log_error("Hết thời gian chờ nhận dữ liệu.", 3001)

        except UnicodeDecodeError as error:
            return await log_error(f"Lỗi giải mã Unicode: {error}", 4001)

        except Exception as error:
            return await log_error(f"Lỗi khi nhận dữ liệu: {error}", 5001)



class PacketHandler:
    """Xử lý dữ liệu, bao gồm mã hóa/giải mã, sử dụng ClientTransport để gửi/nhận."""

    def __init__(self, transport: ClientTransport, encoding: str = 'utf-8') -> None:
        self.encoding = encoding
        self.transport = transport

    async def _process_received_data(self, data: bytes) -> dict:
        """Xử lý và giải mã dữ liệu nhận được."""
        try:
            decoded_data = json.loads(data.decode(self.encoding))
            await logger.log(f"Dữ liệu đã xử lý: {decoded_data}")
            return ResultBuilder.success(9502, data=decoded_data)

        except json.JSONDecodeError as error:
            return await log_error(f"Lỗi giải mã JSON: {error}", 2001)

    async def _prepare_data(self, data: Union[str, dict, list, int, float]) -> Optional[bytes]:
        """Chuyển đổi dữ liệu sang dạng bytes để gửi."""
        if isinstance(data, bytes):
            return data

        try:
            if isinstance(data, str):
                return data.encode(self.encoding)
            if isinstance(data, (list, tuple, dict)):
                return json.dumps(data).encode(self.encoding)
            if isinstance(data, (int, float)):
                return str(data).encode(self.encoding)

            await logger.log("Loại dữ liệu không được hỗ trợ.", level="ERROR")
            return None

        # Bắt lỗi TypeError nếu có lỗi khi chuyển đổi kiểu dữ liệu
        except (TypeError, ValueError) as e:
            await logger.log(f"Lỗi trong quá trình chuyển đổi dữ liệu: {e}", level="ERROR")
            return None

        # Bắt lỗi khi mã hóa chuỗi sang bytes gặp vấn đề
        except UnicodeEncodeError as e:
            await logger.log(f"Lỗi mã hóa chuỗi: {e}", level="ERROR")
            return None

    async def send(self, data: Optional[Union[str, dict, list, int, float]]) -> Optional[dict]:
        """Chuẩn bị và gửi dữ liệu dưới nhiều định dạng khác nhau."""
        if data is None:
            await logger.log("Không có dữ liệu để gửi.", level="WARNING")
            return

        try:
            encoded_data = await self._prepare_data(data)  # Await here to ensure proper execution
            if isinstance(encoded_data, bytes):
                self.transport.send_buffer.extend(encoded_data)
                return await self.transport.send_data()  # Send the data

        except Exception as error:
            return await log_error(f"Lỗi chuẩn bị gửi: {error}", 5001)

    async def receive(self) -> Optional[dict]:
        """Nhận dữ liệu và xử lý nó."""
        response = await self.transport.receive_data()

        if response and "data" in response:
            return await self._process_received_data(response["data"])

        return response