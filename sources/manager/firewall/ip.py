# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import json
import asyncio
import datetime
import aiofiles
import collections

from sources import configs
from sources.utils.logger import AsyncLogger



class IPFirewall:
    """
    Implements an IP rate-limiting firewall to prevent abuse.
    Small system: MAX_REQUESTS = 50, REQUEST_WINDOW = 5 seconds
    Medium system: MAX_REQUESTS = 100, REQUEST_WINDOW = 5 seconds
    Large system: MAX_REQUESTS = 200, REQUEST_WINDOW = 10 seconds
    """
    MAX_REQUESTS = 50  # Maximum allowed requests in 5 seconds
    REQUEST_WINDOW = 5  # Time window in 5 seconds
    BLOCK_TIME = datetime.timedelta(minutes=10)  # Time duration for auto-unblocking

    def __init__(self):
        self.block_ips: set = set()  # Set to hold blocked IP addresses
        self.block_ips_lock = asyncio.Lock()
        self.auto_unblock_event = asyncio.Event()
        self.block_file = configs.file_paths('block.txt')
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
        """Load blocked IP addresses from a file."""
        try:
            async with aiofiles.open(self.block_file, mode='r') as file:
                async for line in file:
                    try:
                        ip, block_time_str = line.strip().split(',')
                        block_time = datetime.datetime.strptime(block_time_str, '%Y-%m-%d %H:%M:%S')
                        self.block_ips.add(ip)
                        self.ip_requests[ip].append(block_time)
                    except ValueError as e:
                        await AsyncLogger.notify_error(f"Error parsing block time for IP: {ip} - {e}")
        except FileNotFoundError:
            await AsyncLogger.notify_error("Blocked IPs file not found. Starting with no blocked IPs.")
        except Exception as e:
            await AsyncLogger.notify_error(f"Error loading blocked IPs: {e}")

    async def track_requests(self, ip_address: str):
        """Track the number of requests from an IP and log if necessary."""
        current_time = datetime.datetime.now()

        if ip_address not in self.ip_requests:
            self.ip_requests[ip_address] = []

        # Filter requests within REQUEST_WINDOW
        self.ip_requests[ip_address] = [
            req_time for req_time in self.ip_requests[ip_address]
            if (current_time - req_time).total_seconds() < IPFirewall.REQUEST_WINDOW
        ]

        self.ip_requests[ip_address].append(current_time)

        # Check if too many requests have occurred within REQUEST_WINDOW
        if len(self.ip_requests[ip_address]) > IPFirewall.MAX_REQUESTS:
            await AsyncLogger.notify_info(f"Warning: {ip_address} has exceeded request limits.")
            self.ip_requests[ip_address] = [current_time]  # Reset the timestamp to current time

            # Save the blocked IPs to the file
            await self._save_block_ips()

    async def auto_unblock_ips(self):
        """Automatically unblock IPs after the BLOCK_TIME has passed."""
        while not self.auto_unblock_event.is_set():
            try:
                current_time = datetime.datetime.now()

                async with self.block_ips_lock:
                    for ip in list(self.block_ips):
                        block_time = self.ip_requests[ip][0]

                        if isinstance(block_time, str):
                            try:
                                block_time = datetime.datetime.strptime(block_time, "%Y-%m-%d %H:%M:%S")
                                self.ip_requests[ip][0] = block_time
                            except ValueError as e:
                                await AsyncLogger.notify_error(f"Error converting block time for IP: {ip} - {e}")
                                continue

                        if (current_time - block_time).total_seconds() > IPFirewall.BLOCK_TIME.total_seconds():
                            self.block_ips.remove(ip)
                            await AsyncLogger.notify_info(f"Unblocked IP: {ip}")
                            await self._save_block_ips()

            except Exception as e:
                await AsyncLogger.notify_error(f"Error in auto-unblock process: {e}")

            await asyncio.sleep(60 * 5)  # Check every 5 minutes

    def remaining_time(self, ip_address: str) -> bytes:
        """Calculate the remaining block time for an IP and return as a JSON-encoded bytes object."""
        result = {
            "status": True,
            "ip": ip_address,
            "message": "No longer blocked",
            "remaining_time": "00:00:00"
        }

        if ip_address in self.block_ips:
            block_start_time = self.ip_requests[ip_address][0]
            elapsed_time = datetime.datetime.now() - block_start_time
            remaining_time = self.BLOCK_TIME - elapsed_time

            if remaining_time.total_seconds() > 0:
                result["status"] = False
                result["message"] = "IP is blocked"
                result["remaining_time"] = str(remaining_time)

        return json.dumps(result).encode()

    async def close(self):
        """Stop the auto_unblock_ips coroutine gracefully."""
        self.auto_unblock_event.set()  # Set the event to stop auto-unblocking
        await asyncio.sleep(1)  # Small delay to ensure current tasks finish
