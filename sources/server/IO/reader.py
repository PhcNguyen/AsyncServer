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

    async def receive_data(self) -> (bytes | int):
        """Nhận dữ liệu từ luồng một cách bất đồng bộ."""
        try:
            data = await asyncio.wait_for(
                self.reader.read(self.buffer_size), timeout=self.timeout
            )

            if data:  # Kiểm tra nếu dữ liệu không trống
                await Logger.info(f"Nhận được {len(data)} bytes dữ liệu.", False)
                return data

            # Nếu dữ liệu nhận được là rỗng
            await Logger.info("Không có dữ liệu nhận được (dữ liệu trống).", False)
            return 5005

        except asyncio.TimeoutError:
            await Logger.error("Hết thời gian chờ nhận dữ liệu.", False)
            return 3001

        except ConnectionResetError:
            await Logger.error("Kết nối bị thiết lập lại bởi client.", False)
            return 1001

        except OSError as os_error:
            await Logger.error(f"Lỗi hệ điều hành khi nhận dữ liệu: {str(os_error)}", False)
            return 5001

        except Exception as error:
            await Logger.error(f"Nhận dữ liệu: {str(error)}", False)
            return 5001