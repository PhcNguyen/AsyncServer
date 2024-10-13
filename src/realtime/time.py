# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

from datetime import datetime


def formatted_time() -> str:
    """Return: 13/10/24 14:30"""
    now = datetime.now()
    return f"{now.day}/{now.month}/{now.year % 100:02d} {now.hour:02d}:{now.minute:02d}"