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

CHUNK_SIZE = 8192  # 8KB

async def send_large_data(writer, data: bytes):
    data_length = len(data)
    total_chunks = (data_length + CHUNK_SIZE - 1) // CHUNK_SIZE

    for i in range(total_chunks):
        start = i * CHUNK_SIZE
        end = start + CHUNK_SIZE
        chunk = data[start:end]

        # Gửi độ dài của gói tin và gói tin tương ứng
        chunk_length = len(chunk).to_bytes(4, 'big')
        writer.write(chunk_length + chunk)
        await writer.drain()

async def receive_large_data(reader):
    data = bytearray()
    while True:
        # Đọc độ dài của từng gói tin
        chunk_length = int.from_bytes(await reader.readexactly(4), 'big')
        if chunk_length == 0:
            break

        # Đọc gói tin tương ứng
        chunk = await reader.readexactly(chunk_length)
        data.extend(chunk)

    return bytes(data)



class Transport:
    """Xử lý dữ liệu, bao gồm mã hóa/giải mã, sử dụng Reader, Writer để gửi/nhận."""

    def __init__(self, reader: asyncio.StreamReader = None, writer: asyncio.StreamWriter = None, encoding: str = 'utf-8') -> None:
        self.encoding = encoding
        self.writer = Writer(writer, 8192)
        self.reader = Reader(reader, 120, 8192)

    async def process_received_data(self, data: bytes) -> List[Union[int, str, str]]:
        """Xử lý và giải mã dữ liệu nhận được."""
        command = int.from_bytes(data[0:1], 'big', signed=True)  # Lệnh 1 byte

        # Kiểm tra lệnh có nằm trong khoảng hợp lệ không
        if not -128 <= command <= 127:
            await Logger.error(f"Command không hợp lệ: {command}.", False)
            return [6001, None, None]

        # Giải mã dữ liệu và kiểm tra xem có hợp lệ không
        if (decoded_data := DataPackager(self.encoding).decode(data[1:])) == b'\x80':
            await Logger.error("Loại dữ liệu không được hỗ trợ.", False)
            return [4001, None, None]

        await Logger.info(f"Dữ liệu đã xử lý: {decoded_data}", False)
        return [9502, command, decoded_data]

    async def prepare_data(self, data: Union[str, dict, list, int, float]) -> bytes:
        """Chuyển đổi dữ liệu sang dạng bytes để gửi."""
        if isinstance(data, bytes):
            return data

        try:
            if (data := DataPackager(self.encoding).encode(data)) == b'\x80':
                await Logger.error("Loại dữ liệu không được hỗ trợ.", False)
                return b'\x80'
            return data

        except (TypeError, ValueError, UnicodeEncodeError) as e:
            await Logger.error(f"Chuyển đổi dữ liệu: {e}", False)
            return b'\x80'

    async def send(self, data: Optional[Union[str, dict, list, int, float, bytes]]) -> int:
        """Chuẩn bị và gửi lệnh dưới nhiều định dạng khác nhau."""
        if data is None:
            await Logger.warning("Không có dữ liệu để gửi.")
            return 2001

        try:
            # Chuyển đổi dữ liệu sang bytes nếu không phải là bytes
            if not isinstance(data, bytes):
                if (data :=  await self.prepare_data(data)) == b'\x80':
                    return 4002

            # Gửi dữ liệu nếu là bytes
            if isinstance(data, bytes):
                self.writer.send_buffer.extend(data)
                return await self.writer.send_data()

        except Exception as error:
            await Logger.error(f"Lỗi chuẩn bị gửi: {error}", False)

        return 5002  # Trả về mã lỗi mặc định

    async def receive(self) -> List[Union[int, str, bytes]]:
        """Nhận dữ liệu và xử lý nó."""
        result: (bytes | int) = await self.reader.receive_data()
        return await self.process_received_data(result) \
        if isinstance(result, bytes) else [result, None, None]