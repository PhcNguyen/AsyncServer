# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import asyncio
import aiofiles
import collections

from sources.model.realtime import Realtime
from sources.application.configs import Configs
from sources.model.logging.serverlogger import AsyncLogger

MAX_REQUESTS = 10  # Maximum allowed requests in 5 seconds
REQUEST_WINDOW = 5  # Time window in 5 seconds
BLOCK_TIME = Realtime.timedelta(days=1)  # Time duration for auto-unblocking


class FireWall:
    def __init__(self):
        self.block_ips: set = set()  # Set to hold blocked IP addresses
        self.block_ips_lock = asyncio.Lock()
        self.auto_unblock_event = asyncio.Event()
        self.block_file = Configs.DirPath.block_file
        self.ip_requests = collections.defaultdict(list)  # Track requests per IP (IP: [timestamps])

        # Load blocked IPs at initialization
        asyncio.run(self._load_block_ips())

    async def _save_block_ips(self):
        """Save blocked IP addresses to a file with timestamps."""
        async with self.block_ips_lock:  # Ensure only one task writes to the file at a time
            async with aiofiles.open(self.block_file, mode='w') as file:
                for ip in self.block_ips:
                    block_time = self.ip_requests[ip][0].strftime('%Y-%m-%d %H:%M:%S')
                    await file.write(f"{ip},{block_time}\n")

    async def _load_block_ips(self):
        try:
            async with aiofiles.open(self.block_file, mode='r') as file:
                async for line in file:
                    try:
                        ip, block_time_str = line.strip().split(',')
                        block_time = Realtime.strptime(block_time_str, '%Y-%m-%d %H:%M:%S')
                        self.block_ips.add(ip)
                        self.ip_requests[ip].append(block_time)
                    except ValueError as e:
                        await AsyncLogger.notify_error(f"Error parsing block time for IP: {ip} - {e}")
        except FileNotFoundError:
            await AsyncLogger.notify_error("Blocked IPs file not found. Starting with no blocked IPs.")
        except Exception as e:
            await AsyncLogger.notify_error(f"Error loading blocked IPs: {e}")

    async def track_requests(self, ip_address: str):
        """Track the number of requests from an IP and block if necessary."""
        current_time = Realtime.now()  # Lấy thời gian hiện tại

        # Filter requests within the REQUEST_WINDOW
        self.ip_requests[ip_address] = [
            req_time for req_time in self.ip_requests[ip_address]
            if (current_time - req_time).total_seconds() < REQUEST_WINDOW
        ]

        # Add the current request time to the list
        self.ip_requests[ip_address].append(current_time)

        # If more than MAX_REQUESTS are made within REQUEST_WINDOW, block the IP
        if len(self.ip_requests[ip_address]) > MAX_REQUESTS:
            self.block_ips.add(ip_address)
            self.ip_requests[ip_address] = [current_time]  # Save the block time for unblock
            await AsyncLogger.notify(f"Blocked IP: {ip_address}")

            await self._save_block_ips()  # Ensure it saves immediately

    async def auto_unblock_ips(self):
        """Automatically unblock IPs after the BLOCK_TIME has passed."""
        while not self.auto_unblock_event.is_set():  # Check the event
            try:
                current_time = Realtime.now()

                for ip in list(self.block_ips):  # Create a copy to modify safely
                    block_time = self.ip_requests[ip][0]

                    if isinstance(block_time, str):
                        try:
                            block_time = Realtime.strptime(block_time, "%Y-%m-%d %H:%M:%S")
                            self.ip_requests[ip][0] = block_time  # Ensure it's stored as datetime
                        except ValueError as e:
                            await AsyncLogger.notify_error(f"Error converting block time for IP: {ip} - {e}")
                            continue  # Skip this IP if there's an error

                    # Unblock IPs that have been blocked for more than BLOCK_TIME
                    if (current_time - block_time).total_seconds() > BLOCK_TIME.total_seconds():
                        self.block_ips.remove(ip)
                        await AsyncLogger.notify(f"Unblocked IP: {ip}")

                        await self._save_block_ips()  # Save changes immediately

            except Exception as e:
                await AsyncLogger.notify_error(f"Error in auto-unblock process: {e}")

            await asyncio.sleep(60 * 5)  # Check every 5 minutes

    async def close(self):
        """Stop auto_unblock_ips gracefully."""
        self.auto_unblock_event.set()  # Set the event to stop auto-unblocking
        await asyncio.sleep(1)  # Small delay to ensure current tasks finish