# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

from sources import configs
from sources.manager.files import iofiles
from sources.model.logging.serverlogger import AsyncLogger



async def queries_line(line_number: int) -> (str | None):
    """Read specific line from queries file."""
    try:
        content = await iofiles.read_files(configs.file_paths('queries.sql'), mode='r')
        valid_lines = [line.strip() for line in content.split(';') if line.strip()]

        if valid_lines and 1 <= line_number <= len(valid_lines):
            return valid_lines[line_number - 1].strip() + ';'
        await AsyncLogger.notify_error("Invalid line number.")
        return None
    except Exception as error:
        await AsyncLogger.notify_error(error)
        return None