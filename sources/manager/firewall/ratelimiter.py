# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import datetime

from collections import defaultdict



class RateLimiter:
    def __init__(self, limit: int, period: int):
        self.limit = limit  # Giới hạn số yêu cầu
        self.period = period  # Thời gian trong giây
        self.requests = defaultdict(list)  # Lưu trữ thời gian yêu cầu từ mỗi IP

    async def is_allowed(self, ip_address: str):
        current_time = datetime.datetime.now()
        # Lọc các yêu cầu cũ
        self.requests[ip_address] = [
            request_time for request_time in self.requests[ip_address]
            if (current_time - request_time).total_seconds() < self.period
        ]
        # Kiểm tra số yêu cầu hiện tại
        if len(self.requests[ip_address]) < self.limit:
            self.requests[ip_address].append(current_time)
            return True
        return False
