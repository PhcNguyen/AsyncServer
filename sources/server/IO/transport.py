# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import asyncio

from typing import Optional, Union, List
from sources.utils.logger import Logger
from sources.server.IO.write import Writer
from sources.server.IO.reader import Reader
from sources.server.IO.packager import DataPackager


# command -128 -> 127
def create_command(command: int, data: bytes) -> bytes:
    """Tạo một lệnh có cấu trúc để gửi với lệnh 1 byte và payload không giới hạn."""
    return (
        command.to_bytes(1, 'big', signed=True) +  # 1 byte cho lệnh
        data  # Không giới hạn số byte cho data
    )





class Transport:
    """Xử lý dữ liệu, bao gồm mã hóa/giải mã, sử dụng Reader, Writer để gửi/nhận."""

    def __init__(self, reader: asyncio.StreamReader = None, writer: asyncio.StreamWriter = None, encoding: str = 'utf-8') -> None:
        self.encoding = encoding
        self.writer = Writer(writer)
        self.reader = Reader(reader)

    async def process_received_data(self, data: bytes) -> List[Union[int, str, bytes]]:
        """Xử lý và giải mã dữ liệu nhận được."""
        command = int.from_bytes(data[0:1], 'big', signed=True)  # Lệnh 1 byte

        # Kiểm tra xem command có nằm trong khoảng -128 đến 127 không
        if command < -128 or command > 127:
            await Logger.error(f"Command không hợp lệ: {command}.", False)
            return [6001, data, command]  # Trả về với data là bytes

        try:
            decoded_data = DataPackager(self.encoding).decode(data[1:]) # Giải mã dữ liệu
            await Logger.info(f"Dữ liệu đã xử lý: {decoded_data}", False)
            return [9502, decoded_data, command]  # Trả về với decoded_data là str

        except UnicodeDecodeError as error:
            await Logger.error(f"Lỗi giải mã data: {error}", False)
            return [4001, data[1:], command]  # Trả về với data[1:] là bytes

    async def prepare_data(self, data: Union[str, dict, list, int, float]) -> Optional[bytes]:
        """Chuyển đổi dữ liệu sang dạng bytes để gửi."""
        if isinstance(data, bytes):
            return data

        try:
            if (data := DataPackager(self.encoding).encode(data)) == b'\x80':
                await Logger.error("Loại dữ liệu không được hỗ trợ.", False)
                return b''
            return data

        except (TypeError, ValueError) as e:
            await Logger.error(f"Lỗi trong quá trình chuyển đổi dữ liệu: {e}", False)
            return b''

        except UnicodeEncodeError as e:
            await Logger.error(f"Lỗi mã hóa chuỗi: {e}", False)
            return b''

    async def send(self, data: Optional[Union[str, dict, list, int, float]]) -> List[Union[int, str, bytes]]:
        """Chuẩn bị và gửi lệnh dưới nhiều định dạng khác nhau."""
        if data is None:
            await Logger.warning("Không có dữ liệu để gửi.")
            return []

        try:
            encoded_data = await self.prepare_data(data)  # Chuyển đổi dữ liệu sang bytes

            if isinstance(encoded_data, bytes):
                self.writer.send_buffer.extend(encoded_data)
                code = await self.writer.send_data()  # Gửi dữ liệu
                return [code, encoded_data, 128]

        except Exception as error:
            await Logger.error(f"Lỗi chuẩn bị gửi: {error}", False)
            return [5002, data, 128]

    async def receive(self) -> List[Union[int, str, bytes]]:
        """Nhận dữ liệu và xử lý nó."""
        result: bytes = await self.reader.receive_data()

        if len(result) > 0:
            return await self.process_received_data(result)

        return [2001, result, 128]