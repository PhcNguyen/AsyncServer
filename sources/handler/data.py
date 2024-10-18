# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import json
import asyncio

from sources.model.logging import AsyncLogger



class DataHandler:
    BUFFER_SIZE = 8192  # Chuyển thành hằng số lớp

    def __init__(self, transport = None):
        self.transport = transport
        self.bytes_sent = 0
        self.bytes_received = 0
        self.send_buffer = bytearray()

    async def _try_send(self):
        while self.send_buffer:
            try:
                sent = self.transport.send(self.send_buffer)
                self.bytes_sent += sent
                self.send_buffer = self.send_buffer[sent:]
                await AsyncLogger.notify(f"Sent {sent} bytes.")
            except Exception as e:
                await AsyncLogger.notify_error(f"Error during send: {e}")
                break

    async def send(self, data):
        if isinstance(data, str):                    # Kiểm tra nếu data là chuỗi
            data = data.encode('utf-8')              # Chuyển đổi thành bytes
        elif isinstance(data, (list, tuple, dict)):  # Nếu data là list hoặc tuple or dict
            data = json.dumps(data).encode('utf-8')  # Chuyển list/tuple/dict thành JSON rồi mã hóa thành bytes
        elif isinstance(data, (int, float)):         # Nếu data là số
            data = str(data).encode('utf-8')         # Chuyển số thành chuỗi rồi mã hóa thành bytes

        self.send_buffer.extend(data)
        await self._try_send()

    async def receive(self):
        while True:
            try:
                data = await asyncio.wait_for(self.transport.read(self.BUFFER_SIZE), timeout=1.0)
                if not data:
                    return None
                try:
                    decoded_data = json.loads(data.decode('utf-8'))  # Giải mã JSON từ chuỗi byte
                    data = decoded_data  # Gán lại vào biến data
                except json.JSONDecodeError as json_error:
                    error_message = f"JSON decode error: {json_error}"
                    await AsyncLogger.notify_error(error_message)

                    # Gửi thông báo lỗi về phía client
                    await self.send({
                        "status": False,
                        "message": error_message
                    })
                    continue  # Tiếp tục vòng lặp để nhận dữ liệu tiếp theo

                self.bytes_received += len(data)
                return data
            except asyncio.TimeoutError:
                continue  # Continue on timeout
            except Exception as e:
                await AsyncLogger.notify_error(f"Error during receive: {e}")
                break