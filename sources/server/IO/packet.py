# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import json
import asyncio

from typing import Optional, Union
from sources.utils.logger import Logger
from sources.server.IO.write import Writer
from sources.server.IO.reader import Reader
from sources.constants.result import ResultBuilder


# command -128 -> 127
def create_command(command: int, payload: bytes) -> bytes:
    """Tạo một lệnh có cấu trúc để gửi với độ dài payload lên đến 2^64 - 1 bytes."""
    length = len(payload)
    return (
        command.to_bytes(1, 'big', signed=True) +
        length.to_bytes(8, 'big') +  # Sử dụng 8 byte cho độ dài
        payload
    )


def parse_command(data: bytes) -> tuple:
    """Phân tích một lệnh nhận được thành các thành phần của nó."""
    command = int.from_bytes(data[0:1], 'big', signed=True)  # Lệnh 1 byte
    length = int.from_bytes(data[1:9], 'big')  # Sử dụng 8 byte cho độ dài
    payload = data[9:9 + length]  # Nội dung dữ liệu
    return command, payload



class PacketHandler:
    """Xử lý dữ liệu, bao gồm mã hóa/giải mã, sử dụng Reader, Writer để gửi/nhận."""

    def __init__(self, reader: asyncio.StreamReader = None, writer: asyncio.StreamWriter = None, encoding: str = 'utf-8') -> None:
        self.encoding = encoding
        self.writer = Writer(writer)
        self.reader = Reader(reader)

    async def process_received_data(self, data: bytes) -> dict:
        """Xử lý và giải mã dữ liệu nhận được."""
        command, payload = parse_command(data)  # Phân tích dữ liệu
        try:
            decoded_data = json.loads(payload.decode(self.encoding))  # Giải mã payload
            await Logger.info(f"Dữ liệu đã xử lý: {decoded_data}", False)
            return ResultBuilder.success(9502, data=decoded_data, command=command)

        except json.JSONDecodeError as error:
            await Logger.error(f"Lỗi giải mã JSON: {error}", False)
            return ResultBuilder.error(2001)

    async def prepare_data(self, data: Union[str, dict, list, int, float]) -> Optional[bytes]:
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

            await Logger.error("Loại dữ liệu không được hỗ trợ.", False)
            return None

        except (TypeError, ValueError) as e:
            await Logger.error(f"Lỗi trong quá trình chuyển đổi dữ liệu: {e}", False)
            return None

        except UnicodeEncodeError as e:
            await Logger.error(f"Lỗi mã hóa chuỗi: {e}", False)
            return None

    async def send(self, command: int, data: Optional[Union[str, dict, list, int, float]]) -> Optional[dict]:
        """Chuẩn bị và gửi lệnh dưới nhiều định dạng khác nhau."""
        if data is None:
            await Logger.warning("Không có dữ liệu để gửi.")
            return

        try:
            encoded_data = await self.prepare_data(data)  # Chuyển đổi dữ liệu sang bytes

            if isinstance(encoded_data, bytes):
                command_message = create_command(command, encoded_data)  # Tạo lệnh
                self.writer.send_buffer.extend(command_message)
                code = await self.writer.send_data()  # Gửi dữ liệu
                return ResultBuilder.success(code)

        except Exception as error:
            await Logger.error(f"Lỗi chuẩn bị gửi: {error}", False)
            return ResultBuilder.error(5002)

    async def receive(self) -> Optional[dict]:
        """Nhận dữ liệu và xử lý nó."""
        response: bytes = await self.reader.receive_data()

        if len(response) > 0:
            return await self.process_received_data(response)

        return None