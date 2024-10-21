# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import time
import json
import asyncio

from sources.utils.logger import AsyncLogger



class DataHandler:
    BUFFER_SIZE = 8192  # Buffer size for reading data

    def __init__(self,
        reader: asyncio.StreamReader=None,
        writer:asyncio.StreamWriter=None
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
                    break

                # Write the data from send_buffer and track the bytes sent
                self.writer.write(self.send_buffer)
                await self.writer.drain()
                self.bytes_sent += len(self.send_buffer)
                await AsyncLogger.notify(f"Sent {len(self.send_buffer)} bytes.")

                # Clear the send buffer after successful send
                self.send_buffer.clear()

            except Exception as e:
                await AsyncLogger.notify_error(f"Error during send: {e}")
                break

    async def send(self, data):
        """Send data in different formats (str, dict, list, etc.)."""
        if data is None:
            await AsyncLogger.notify_error("Data is None, nothing to send.")
            return

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
                return  # Exit if the type is unsupported

            # Add the data to the send buffer and attempt to send it
            self.send_buffer.extend(data)
            await self._try_send()

        except Exception as e:
            await AsyncLogger.notify_error(f"Error during send preparation: {e}")

    async def receive(self):
        """Receive and process data from transport."""
        while True:
            try:
                # Ensure transport (reader) is available
                if self.reader is None:
                    await AsyncLogger.notify_error("No transport available.")
                    return None  # Return None if transport is not available

                # Read data from transport with a timeout
                data = await asyncio.wait_for(self.reader.read(self.BUFFER_SIZE), timeout=60.0)

                # If data is not empty, try to decode it
                if data.strip():
                    try:
                        if isinstance(data, bytes):  # If data is bytes
                            data = data.decode('utf-8')  # Convert to string
                        decoded_data = json.loads(data)
                        # Return the decoded data to the caller (server)
                        return decoded_data  # Return decoded data if successful
                    except json.JSONDecodeError as error:
                        # If JSON decoding fails, log the error but continue receiving
                        return {
                            "status": False,
                            "message": f"{error}"
                        }

                time.sleep(0.1)
            except asyncio.TimeoutError:
                # await AsyncLogger.notify("Timeout occurred while waiting for data.")
                continue

            except UnicodeDecodeError as e:
                # Handle cases where received data isn't valid UTF-8
                await AsyncLogger.notify_error(f"Unicode decode error: {e}")
                continue

            except Exception as e:
                # Handle any other exceptions during receive
                await AsyncLogger.notify_error(f"Error during receive: {e}")
                break  # Stop receiving if an unexpected error occurs
