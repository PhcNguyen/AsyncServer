# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import asyncio
import datetime

from collections import defaultdict



class RateLimiter:
    def __init__(self, limit: int, period: int, lockout_period: int = 300):
        """
        :param limit: Giới hạn số yêu cầu trong khoảng thời gian period.
        :param period: Thời gian tính bằng giây để reset giới hạn yêu cầu.
        :param lockout_period: Thời gian khóa IP khi bị vượt quá giới hạn (tính bằng giây, mặc định là 300 giây = 5 phút).
        """
        self.limit = limit
        self.period = period
        self.running = False
        self.blocked_ips = {}
        self.lock = asyncio.Lock()
        self.requests = defaultdict(list)
        self.lockout_period = lockout_period

    async def is_allowed(self, ip_address: str) -> bool:
        """Kiểm tra xem yêu cầu từ IP có được cho phép hay không."""
        if not isinstance(ip_address, str):
            raise ValueError("IP address must be a string.")

        current_time = datetime.datetime.now()

        async with self.lock:  # Bảo vệ truy cập đồng thời
            # Kiểm tra xem IP có bị khóa không
            if ip_address in self.blocked_ips:
                block_end_time = self.blocked_ips[ip_address]
                if current_time < block_end_time:
                    return False  # IP vẫn bị khóa
                else:
                    del self.blocked_ips[ip_address]  # Hết thời gian khóa, xóa khỏi danh sách

            # Lọc các yêu cầu cũ
            self.requests[ip_address] = [
                request_time for request_time in self.requests[ip_address]
                if (current_time - request_time).total_seconds() < self.period
            ]

            # Kiểm tra số yêu cầu hiện tại
            if len(self.requests[ip_address]) < self.limit:
                self.requests[ip_address].append(current_time)  # Thêm thời gian yêu cầu mới
                return True
            else:
                # Khóa IP trong thời gian lockout_period
                self.blocked_ips[ip_address] = current_time + datetime.timedelta(seconds=self.lockout_period)
                return False

    async def clean_inactive_ips(self):
        """Loại bỏ các IP không gửi yêu cầu trong thời gian dài."""
        while self.running:
            current_time = datetime.datetime.now()
            inactive_ips = [
                ip for ip, times in self.requests.items()
                if all((current_time - t).total_seconds() >= self.period for t in times)
            ]
            for ip in inactive_ips: del self.requests[ip]