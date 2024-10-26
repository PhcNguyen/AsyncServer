import asyncio
from sources.utils.logger import Logger



class Writer:
    """Quản lý việc ghi dữ liệu vào luồng bất đồng bộ."""

    def __init__(self, stream_writer: asyncio.StreamWriter, buffer_size=8192) -> None:
        if buffer_size <= 0:
            raise ValueError("Kích thước bộ đệm phải lớn hơn 0.")
        self.bytes_sent = 0
        self.writer = stream_writer
        self.buffer_size = buffer_size
        self.send_buffer = bytearray(buffer_size)

    def append(self, data: bytes) -> None:
        """Thêm dữ liệu vào bộ đệm gửi."""
        self.send_buffer.extend(data)

    def get_bytes_sent(self) -> int:
        """Trả về tổng số byte đã gửi."""
        return self.bytes_sent

    def is_buffer_full(self) -> bool:
        """Kiểm tra xem bộ đệm đã đầy chưa."""
        return len(self.send_buffer) >= self.buffer_size

    async def send_data(self) -> int:
        """Gửi dữ liệu từ bộ đệm một cách bất đồng bộ."""

        # Kiểm tra tính hợp lệ của writer
        if not self.writer or not self.writer.can_write_eof():
            await Logger.error("Writer không khả dụng.", False)
            return 1001

        if not self.send_buffer:
            await Logger.info("Bộ đệm trống, không có dữ liệu để gửi.", False)
            return 1002

        while self.send_buffer:
            try:
                # Xác định số bytes cần gửi
                bytes_to_send = min(len(self.send_buffer), self.buffer_size)

                # Ghi dữ liệu vào writer
                self.writer.write(self.send_buffer[:bytes_to_send])
                await self.writer.drain()

                # Cập nhật số bytes đã gửi
                self.bytes_sent += bytes_to_send
                del self.send_buffer[:bytes_to_send]  # Xóa phần dữ liệu đã gửi

                # Log thông tin đã gửi
                await Logger.info(
                    f"Đã gửi {bytes_to_send} bytes. Tổng cộng: {self.bytes_sent} bytes.",
                    False
                )
                return 9501

            except OSError as error:
                # Log lỗi OSError với mã lỗi
                await Logger.error(f"OSError: {str(error)}, Mã lỗi: {error.errno}", False)
                return 5002 if error.errno == 64 else 5003

            except Exception as error:
                # Log lỗi không xác định
                await Logger.error(f"Lỗi không xác định: {str(error)}", False)
                return 5004