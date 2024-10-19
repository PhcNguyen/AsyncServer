# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

from datetime import datetime, timedelta, timezone



class TimeUtil:
    """Class để quản lý các chức năng liên quan đến thời gian."""
    SECOND = 1
    MINUTE = 2
    HOUR = 3
    DAY = 4
    WEEK = 5
    MONTH = 6
    YEAR = 7

    @staticmethod
    def now_vietnam() -> datetime:
        """Lấy thời gian hiện tại theo giờ Việt Nam (UTC+7)."""
        return datetime.now(timezone(timedelta(hours=7)))

    @staticmethod
    def to_vietnam(utc_time: datetime) -> datetime:
        """Chuyển đổi thời gian UTC sang giờ Việt Nam."""
        return utc_time.astimezone(timezone(timedelta(hours=7)))

    @staticmethod
    def since(last_time: datetime) -> float:
        """Tính khoảng thời gian đã trôi qua tính bằng giây."""
        return (TimeUtil.now_vietnam() - last_time).total_seconds()

    @staticmethod
    def diff_date(d1: datetime, d2: datetime, time_type: int) -> int:
        """
        Tính khoảng cách giữa hai thời điểm d1 và d2 theo loại thời gian được chỉ định.

        :param d1: Thời gian bắt đầu
        :param d2: Thời gian kết thúc
        :param time_type: Loại thời gian (giây, phút, giờ, ngày, tuần, tháng, năm)
        :return: Khoảng cách thời gian theo loại
        """
        time_diff = abs(int((d1 - d2).total_seconds()))  # Tính khoảng cách thời gian tính bằng giây

        # Tính khoảng cách theo loại thời gian
        if time_type == TimeUtil.SECOND:
            return time_diff
        elif time_type == TimeUtil.MINUTE:
            return time_diff // 60
        elif time_type == TimeUtil.HOUR:
            return time_diff // 3600
        elif time_type == TimeUtil.DAY:
            return time_diff // 86400
        elif time_type == TimeUtil.WEEK:
            return time_diff // 604800
        elif time_type == TimeUtil.MONTH:
            return time_diff // 2592000  # Giả sử 1 tháng có 30 ngày
        elif time_type == TimeUtil.YEAR:
            return time_diff // 31536000  # Giả sử 1 năm có 365 ngày
        else:
            return 0

    @staticmethod
    def is_time_now_in_range(start_time: str, end_time: str, date_format: str) -> bool:
        """
        Kiểm tra xem thời gian hiện tại có nằm trong khoảng thời gian giữa start_time và end_time không.

        :param start_time: Thời gian bắt đầu
        :param end_time: Thời gian kết thúc
        :param date_format: Định dạng thời gian
        :return: True nếu thời gian hiện tại nằm trong khoảng, False nếu không
        """
        try:
            start = datetime.strptime(start_time, date_format)  # Chuyển đổi chuỗi thành datetime
            end = datetime.strptime(end_time, date_format)
            now = datetime.now()
            return start < now < end
        except ValueError:
            raise Exception("Thời gian không hợp lệ")

    @staticmethod
    def get_curr_day() -> int:
        """
        Lấy ngày hiện tại.

        :return: Ngày trong tháng (0-6, trong đó 0 là Chủ nhật)
        """
        return datetime.now().day

    @staticmethod
    def get_curr_hour() -> int:
        """
        Lấy giờ hiện tại.

        :return: Giờ hiện tại (0-23)
        """
        return datetime.now().hour

    @staticmethod
    def get_curr_min() -> int:
        """
        Lấy phút hiện tại.

        :return: Phút hiện tại (0-59)
        """
        return datetime.now().minute

    @staticmethod
    def get_time_left(last_time: float, target_seconds: int) -> str:
        """
        Tính thời gian còn lại từ last_time đến target_seconds.

        :param last_time: Thời gian cuối cùng (được tính bằng millisecond)
        :param target_seconds: Thời gian mục tiêu
        :return: Chuỗi thời gian còn lại
        """
        seconds_passed = (datetime.now() - datetime.fromtimestamp(last_time / 1000)).total_seconds()
        seconds_left = target_seconds - int(seconds_passed)
        seconds_left = max(seconds_left, 0)  # Đảm bảo không âm

        return f"{seconds_left // 60} phút" if seconds_left > 60 else f"{seconds_left} giây"

    @staticmethod
    def get_min_left(last_time: float, target_seconds: int) -> int:
        """
        Tính số phút còn lại từ last_time đến target_seconds.

        :param last_time: Thời gian cuối cùng (được tính bằng millisecond)
        :param target_seconds: Thời gian mục tiêu
        :return: Số phút còn lại
        """
        seconds_passed = (datetime.now() - datetime.fromtimestamp(last_time / 1000)).total_seconds()
        seconds_left = max(0, target_seconds - int(seconds_passed))  # Đảm bảo không âm

        # Sử dụng phép chia và làm tròn lên để tính số phút còn lại
        return (seconds_left + 59) // 60  # Tính số phút còn lại

    @staticmethod
    def get_second_left(last_time: float, target_seconds: int) -> int:
        """
        Tính số giây còn lại từ last_time đến target_seconds.

        :param last_time: Thời gian cuối cùng (được tính bằng millisecond)
        :param target_seconds: Thời gian mục tiêu
        :return: Số giây còn lại
        """
        seconds_passed = (datetime.now() - datetime.fromtimestamp(last_time / 1000)).total_seconds()
        seconds_left = target_seconds - int(seconds_passed)
        return max(seconds_left, 0)  # Đảm bảo không âm

    @staticmethod
    def get_time(time_str: str, date_format: str) -> float:
        """
        Chuyển đổi chuỗi thời gian thành timestamp.

        :param time_str: Chuỗi thời gian
        :param date_format: Định dạng thời gian
        :return: Timestamp của thời gian
        """
        try:
            return datetime.strptime(time_str, date_format).timestamp() * 1000  # Chuyển đổi thành milliseconds
        except ValueError:
            raise Exception("Thời gian không hợp lệ")

    @staticmethod
    def get_time_now(date_format: str) -> str:
        """
        Lấy thời gian hiện tại theo định dạng đã cho.

        :param date_format: Định dạng thời gian
        :return: Thời gian hiện tại dưới dạng chuỗi
        """
        return datetime.now().strftime(date_format)

    @staticmethod
    def get_time_before_current(sub_time: int, date_format: str) -> str:
        """
        Lấy thời gian trước thời điểm hiện tại.

        :param sub_time: Số millisecond cần trừ đi từ thời gian hiện tại
        :param date_format: Định dạng thời gian
        :return: Thời gian trước đó dưới dạng chuỗi
        """
        return (datetime.now() - timedelta(milliseconds=sub_time)).strftime(date_format)

    @staticmethod
    def format_time(time: datetime, date_format: str) -> str:
        """
        Định dạng thời gian từ đối tượng datetime.

        :param time: Đối tượng datetime
        :param date_format: Định dạng thời gian
        :return: Thời gian đã định dạng dưới dạng chuỗi
        """
        return time.strftime(date_format)

    @staticmethod
    def format_time_from_timestamp(timestamp: float, date_format: str) -> str:
        """
        Định dạng thời gian từ timestamp.

        :param timestamp: Timestamp (milliseconds)
        :param date_format: Định dạng thời gian
        :return: Thời gian đã định dạng dưới dạng chuỗi
        """
        return datetime.fromtimestamp(timestamp / 1000).strftime(date_format)
