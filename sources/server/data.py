# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import json
import asyncio

from sources.utils.response import ResponseBuilder
from sources.utils.logger import AsyncLogger



class DataHandler:
    BUFFER_SIZE = 8192  # Buffer size for reading data

    def __init__(self,
        reader: asyncio.StreamReader = None,
        writer: asyncio.StreamWriter = None
    ) -> None:
        """Initialize the DataHandler instance."""
        self.reader = reader  # Use StreamReader for reading
        self.writer = writer  # Use StreamWriter for writing
        self.bytes_sent = 0
        self.bytes_received = 0
        self.send_buffer = bytearray()

    async def _try_send(self):
        """Attempt to send data from the send buffer."""
        while self.send_buffer:
            try:
                # Ensure that transport (writer) is available before attempting to send
                if self.writer is None:
                    await AsyncLogger.notify_error("No transport available.")
                    return ResponseBuilder.error(1001)

                # Write the data from send_buffer and track the bytes sent
                self.writer.write(self.send_buffer)
                await self.writer.drain()
                self.bytes_sent += len(self.send_buffer)
                await AsyncLogger.notify_info(f"Sent {len(self.send_buffer)} bytes.")

                # Clear the send buffer after successful send
                self.send_buffer.clear()
                return ResponseBuilder.success(9501, bytes_sent=self.bytes_sent)

            except OSError as error:
                if error.errno == 64:  # WinError 64
                    await AsyncLogger.notify_error("Network error: The specified network name is no longer available.")
                    return ResponseBuilder.error(5002, error=error)
                else:
                    await AsyncLogger.notify_error(f"Error during send: {error}")
                    return ResponseBuilder.error(5003, error=error)

            except Exception as error:
                await AsyncLogger.notify_error(f"Unexpected error during send: {error}")
                return ResponseBuilder.error(5004, error=error)

    async def receive(self):
        """Receive and process data from transport."""
        while True:
            try:
                if self.reader is None:
                    await AsyncLogger.notify_error("No transport available.")
                    return ResponseBuilder.error(1001)

                # Read data from transport with a timeout
                data = await asyncio.wait_for(self.reader.read(self.BUFFER_SIZE), timeout=1.0)

                if data.strip():
                    try:
                        if isinstance(data, bytes):
                            data = data.decode('utf-8')
                        decoded_data = json.loads(data)
                        return ResponseBuilder.success(9502, data=decoded_data)

                    except json.JSONDecodeError as error:
                        return ResponseBuilder.error(2001, error=error)

                await asyncio.sleep(0.1)
            except asyncio.TimeoutError:
                return ResponseBuilder.error(3001)
            except UnicodeDecodeError as error:
                return ResponseBuilder.error(4001, error=error)
            except Exception as error:
                return ResponseBuilder.error(5001, error=error)

    async def send(self, data):
        """Send data in different formats (str, dict, list, etc.)."""
        if data is None:
            return

        # Handle various data types before sending
        try:
            # Sử dụng prepare_data để chuyển đổi dữ liệu sang bytes
            data = prepare_data(data)

            if isinstance(data, dict) and not data.get("status"):
                # Nếu data là error response từ prepare_data, trả về luôn lỗi
                return ResponseBuilder.error(404, data=data)

            # Add the data to the send buffer and attempt to send it
            self.send_buffer.extend(data)
            send_response = await self._try_send()

            if send_response and not send_response['status']:
                # If there's an error during sending, return the error Message
                return send_response

            return ResponseBuilder.success(9501, bytes_sent=len(data))

        except Exception as error:
            await AsyncLogger.notify_error(f"Error during send preparation: {error}")
            return ResponseBuilder.error(5001, error=error)


def prepare_data(data):
    """Chuyển đổi dữ liệu sang định dạng byte."""
    if isinstance(data, bytes):
        return data  # Không cần chuyển đổi

    # Chuyển đổi các kiểu dữ liệu khác sang bytes
    try:
        return (data.encode('utf-8')
            if isinstance(data, str)
            else json.dumps(data).encode('utf-8')
            if isinstance(data, (list, tuple, dict))
            else str(data).encode('utf-8')
            if isinstance(data, (int, float))
            else json.dumps(data.__dict__).encode('utf-8')
            if hasattr(data, '__dict__')
            else ResponseBuilder.error(4002)
        )
    except Exception as error:
        return ResponseBuilder.error(5001, error=error)  # Xử lý lỗi chuyển đổi