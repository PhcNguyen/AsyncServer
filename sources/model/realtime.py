# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import datetime



class Realtime:
    @staticmethod
    def formatted_time() -> str:
        """Return: 13/10/24 14:30"""
        now = datetime.datetime.now()
        return f"{now.day}/{now.month}/{now.year % 100:02d} {now.hour:02d}:{now.minute:02d}"
    
    @staticmethod
    def timedelta(
        days: float = 0,
        seconds: float = 0,
        microseconds: float = 0,
        milliseconds: float = 0,
        minutes: float = 0,
        hours: float = 0,
        weeks: float = 0
    ) -> datetime.timedelta:
        time = datetime.timedelta(
            days, seconds, microseconds, 
            milliseconds, minutes, hours, weeks
        )
        return time
    
    @staticmethod
    def now(tz=None) -> datetime.datetime:
        """Construct a datetime from time.time() and optional time zone info."""
        return datetime.datetime.now(tz)

    @staticmethod
    def strptime(
        date_string: str,
        format: str,
        /
    ) -> datetime.datetime:
        """string, format -> new datetime parsed from a string (like time.strptime())."""
        return datetime.datetime.strptime(date_string, format)