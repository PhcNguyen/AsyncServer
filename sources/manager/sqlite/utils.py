# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import re

from sources import configs
from sources.manager.files.iofiles import AsyncFileIO
from sources.utils.logger import AsyncLogger



async def queries_line(line_number: int) -> str:
    """Read specific line from queries file."""
    try:
        content = await AsyncFileIO.read_file(configs.file_paths('queries.sql'), mode='r')
        valid_lines = [line.strip() for line in content.split(';') if line.strip()]

        if valid_lines and 1 <= line_number <= len(valid_lines):
            return valid_lines[line_number - 1].strip() + ';'
        await AsyncLogger.notify_error("Invalid line number.")
        return ''
    except Exception as error:
        await AsyncLogger.notify_error(error)
        return ''


def is_valid_email(email: str) -> bool:
    """Kiểm tra xem địa chỉ email có hợp lệ hay không."""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None


def is_valid_password(password: str) -> bool:
    """Check if the password meets the required standards."""
    if len(password) < 8:  # Độ dài tối thiểu
        return False
    if not re.search(r"[A-Z]", password):  # Có chữ hoa
        return False
    if not re.search(r"[a-z]", password):  # Có chữ thường
        return False
    if not re.search(r"[0-9]", password):  # Có số
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):  # Có ký tự đặc biệt
        return False
    return True