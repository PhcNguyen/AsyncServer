# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import json
import asyncio

from typing import Optional, Union
from sources.utils.logger import Logger
from sources.utils.response import ResponseBuilder


logger = Logger("data_handler.log")



class DataHandler:
    BUFFER_SIZE = 8192  # Kích thước bộ đệm để đọc dữ liệu

    def __init__(self, reader: asyncio.StreamReader = None, writer: asyncio.StreamWriter = None) -> None:
        """Khởi tạo phiên bản DataHandler."""
        self.reader = reader
        self.writer = writer
        self.encoding = 'utf-8'
        self.bytes_sent = 0
        self.bytes_received = 0
        self.send_buffer = bytearray()

    async def _process_received_data(self, data):
        """Xử lý dữ liệu nhận được."""
        try:
            if isinstance(data, bytes):
                data = data.decode(self.encoding)
            decoded_data = json.loads(data)
            await logger.log(f"Received data processed successfully: {decoded_data}")
            return ResponseBuilder.success(9502, data=decoded_data)

        except json.JSONDecodeError as error:
            await logger.log(f"JSON decode error: {error}", level="ERROR")
            return ResponseBuilder.error(2001, error=error)

    async def _try_send(self) -> Optional[dict]:
        """Thử gửi dữ liệu từ bộ đệm gửi."""
        if not self.writer:
            await logger.log("Writer is not available.", level="ERROR")
            return ResponseBuilder.error(1001)

        try:
            while self.send_buffer:
                self.writer.write(self.send_buffer)
                await self.writer.drain()

                self.bytes_sent += len(self.send_buffer)
                await logger.log(f"Sent {len(self.send_buffer)} bytes.")
                self.send_buffer.clear()

            return ResponseBuilder.success(9501, bytes_sent=self.bytes_sent)

        except OSError as error:
            await logger.log(f"OSError occurred: {error}", level="ERROR")
            return ResponseBuilder.error(
                5002 if error.errno == 64 else 5003,
                error=error
            )

        except Exception as error:
            await logger.log(f"Error occurred while sending: {error}", level="ERROR")
            return ResponseBuilder.error(5004, error=error)

    async def send(self, data: Optional[dict]) -> Optional[dict]:
        """Gửi dữ liệu ở các định dạng khác nhau (str, dict, list, etc.)."""
        if data is None:
            await logger.log("No data to send.", level="WARNING")
            return
        try:
            data = await prepare_data(data)
            if isinstance(data, dict):
                await logger.log(f"Error preparing data: {data}", level="ERROR")
                return data

            if isinstance(data, bytes):
                self.send_buffer.extend(data)
                await logger.log("Data added to send buffer.")
                return await self._try_send()

        except Exception as error:
            await logger.log(f"Error during send preparation: {error}", level="ERROR")
            return ResponseBuilder.error(5001, error=error)

    async def receive(self):
        """Nhận và xử lý dữ liệu từ transport."""
        if not self.reader:
            await logger.log("Reader is not available.", level="ERROR")
            return ResponseBuilder.error(1001)

        while True:
            try:
                data = await asyncio.wait_for(self.reader.read(self.BUFFER_SIZE), timeout=10.0)
                if data.strip():
                    await logger.log("Data received from transport.")
                    return await self._process_received_data(data)
                await asyncio.sleep(0.1)

            except asyncio.TimeoutError:
                await logger.log("Timeout while receiving data.", level="WARNING")
                return ResponseBuilder.error(3001)

            except UnicodeDecodeError as error:
                await logger.log(f"Unicode decode error: {error}", level="ERROR")
                return ResponseBuilder.error(4001, error=error)

            except Exception as error:
                await logger.log(f"Error during receiving data: {error}", level="ERROR")
                return ResponseBuilder.error(5001, error=error)

async def prepare_data(data, encoding='utf-8') -> Optional[Union[dict, bytes]]:
    """Chuyển đổi dữ liệu sang định dạng bytes sử dụng mã hóa chỉ định."""
    if isinstance(data, bytes):
        return data
    try:
        if isinstance(data, str):
            return data.encode(encoding)
        if isinstance(data, (list, tuple, dict)):
            return json.dumps(data).encode(encoding)
        if isinstance(data, (int, float)):
            return str(data).encode(encoding)
        if hasattr(data, '__dict__'):
            return json.dumps(data.__dict__).encode(encoding)

        await logger.log("Unsupported data type.", level="ERROR")
        return ResponseBuilder.error(4002)  # Unsupported data type

    except Exception as error:
        await logger.log(f"Error in data conversion: {error}", level="ERROR")
        return ResponseBuilder.error(5001, error=error)  # Error in conversion
