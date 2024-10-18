# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import datetime



class Realtime:
    """Class để quản lý các chức năng liên quan đến thời gian."""

    @staticmethod
    def now_vietnam() -> datetime.datetime:
        """Lấy thời gian hiện tại theo giờ Việt Nam (UTC+7)."""
        return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7)))

    @staticmethod
    def to_vietnam(utc_time: datetime.datetime) -> datetime.datetime:
        """Chuyển đổi thời gian UTC sang giờ Việt Nam."""
        return utc_time.astimezone(datetime.timezone(datetime.timedelta(hours=7)))

    @staticmethod
    def since(last_time: datetime.datetime) -> float:
        """Tính khoảng thời gian đã trôi qua tính bằng giây."""
        return (Realtime.now_vietnam() - last_time).total_seconds()