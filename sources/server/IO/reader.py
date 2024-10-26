import asyncio
from sources.utils.logger import Logger



class Reader:
    """Quản lý việc nhận dữ liệu từ luồng bất đồng bộ."""

    def __init__(
        self, stream_reader: asyncio.StreamReader,
        timeout: float = 120.0, buffer_size: int = 8192
    ) -> None:
        if buffer_size <= 0:
            raise ValueError("Kích thước bộ đệm phải lớn hơn 0.")

        self.timeout = timeout
        self.reader = stream_reader
        self.buffer_size = buffer_size
        self.receive_buffer = bytearray(buffer_size)

    def get_buffer_size(self) -> int:
        """Trả về kích thước bộ đệm nhận."""
        return len(self.receive_buffer)

    def is_buffer_empty(self) -> bool:
        """Kiểm tra xem bộ đệm nhận có rỗng không."""
        return not self.receive_buffer

    async def receive_data(self) -> bytes:
        """Nhận dữ liệu từ luồng một cách bất đồng bộ."""
        try:
            data = await asyncio.wait_for(
                self.reader.read(self.buffer_size), timeout=self.timeout
            )
            if data:
                await Logger.info(f"Nhận được {len(data)} bytes dữ liệu.", False)
                return data

            await Logger.info("Không có dữ liệu nhận được (dữ liệu trống).", False)
            return b''  # Trả về byte trống nếu không có dữ liệu

        except asyncio.TimeoutError:
            await Logger.error("Hết thời gian chờ nhận dữ liệu.", False)
            return b''

        except Exception as error:
            await Logger.error(f"Lỗi khi nhận dữ liệu: {str(error)}", False)
            return b''