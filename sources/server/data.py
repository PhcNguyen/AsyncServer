# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import time
import json
import asyncio

from sources.utils.system import Response
from sources.utils.logger import AsyncLogger



class DataHandler:
    BUFFER_SIZE = 8192  # Buffer size for reading data

    def __init__(self,
                 reader: asyncio.StreamReader = None,
                 writer: asyncio.StreamWriter = None) -> None:
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
                    return Response.error("No transport available.", error_code=1001)

                # Write the data from send_buffer and track the bytes sent
                self.writer.write(self.send_buffer)
                await self.writer.drain()
                self.bytes_sent += len(self.send_buffer)
                await AsyncLogger.notify(f"Sent {len(self.send_buffer)} bytes.")

                # Clear the send buffer after successful send
                self.send_buffer.clear()
                return Response.success("Data sent successfully", bytes_sent=self.bytes_sent)

            except OSError as e:
                if e.errno == 64:  # WinError 64
                    await AsyncLogger.notify_error("Network error: The specified network name is no longer available.")
                    return Response.error("Network error: The specified network name is no longer available.", error_code=5002)
                else:
                    await AsyncLogger.notify_error(f"Error during send: {e}")
                    return Response.error(f"Error during send: {e}", error_code=5001)

            except Exception as e:
                await AsyncLogger.notify_error(f"Unexpected error during send: {e}")
                return Response.error(f"Unexpected error during send: {e}", error_code=5001)

    async def receive(self):
        """Receive and process data from transport."""
        while True:
            try:
                if self.reader is None:
                    await AsyncLogger.notify_error("No transport available.")
                    return Response.error("No transport available.", error_code=1001)

                # Read data from transport with a timeout
                data = await asyncio.wait_for(self.reader.read(self.BUFFER_SIZE), timeout=60.0)

                if data.strip():
                    try:
                        if isinstance(data, bytes):
                            data = data.decode('utf-8')
                        decoded_data = json.loads(data)
                        return Response.success("Data received successfully", data=decoded_data)

                    except json.JSONDecodeError as error:
                        return Response.error(f"JSON decoding error: {error}", error_code=2001)

                await asyncio.sleep(0.1)
            except asyncio.TimeoutError:
                return Response.error("Timeout occurred while waiting for data.", error_code=3001)

            except UnicodeDecodeError as error:
                return Response.error(f"Unicode decode error: {error}", error_code=4001)

            except Exception as error:
                return Response.error(f"Unexpected error: {error}", error_code=5001)

    async def send(self, data):
        """Send data in different formats (str, dict, list, etc.)."""
        if data is None:
            await AsyncLogger.notify_error("Data is None, nothing to send.")
            return Response.error("Data is None, nothing to send.", error_code=1001)  # Mã lỗi: Không có dữ liệu để gửi

        # Handle various data types before sending
        try:
            if isinstance(data, str):  # If data is a string
                data = data.encode('utf-8')  # Convert to bytes
            elif isinstance(data, (list, tuple, dict)):  # If data is a list/tuple/dict
                data = json.dumps(data).encode('utf-8')  # Convert to JSON and then to bytes
            elif isinstance(data, (int, float)):  # If data is a number
                data = str(data).encode('utf-8')  # Convert to string and then bytes
            elif isinstance(data, bytes):  # If data is already in bytes
                pass  # No conversion necessary
            else:
                await AsyncLogger.notify_error(f"Unsupported data type: {type(data)}")
                return Response.error(f"Unsupported data type: {type(data)}", error_code=5001)

            # Add the data to the send buffer and attempt to send it
            self.send_buffer.extend(data)
            send_response = await self._try_send()

            if send_response and not send_response['status']:
                # If there's an error during sending, return the error response
                return send_response

            return Response.success("Data sent successfully", bytes_sent=len(data))

        except Exception as e:
            await AsyncLogger.notify_error(f"Error during send preparation: {e}")
            return Response.error(f"Error during send preparation: {e}", error_code=5001)  # Mã lỗi: Lỗi không xác định
