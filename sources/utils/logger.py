# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import os
import logging
import asyncio

from sources.configs import DIR_LOG
from sources.manager.files.filecache import FileCache


def setup_logger() -> logging.Logger:
    """
    Sets up a comprehensive logging configuration with separate files for different log levels
    and a console handler.

    Returns:
        logging.Logger: The configured logger instance.
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)  # Mức tối thiểu để ghi log

    # Formatter sử dụng chung cho cả file và console
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Hàm tạo file handler
    def add_file_handler(level_name: str, level: int) -> None:
        file_path = os.path.join(DIR_LOG, f"{level_name}.log")
        handler = logging.FileHandler(file_path, encoding='utf-8')
        handler.setLevel(level)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # Tạo các file handler cho từng mức log
    add_file_handler('debug', logging.DEBUG)
    add_file_handler('info', logging.INFO)
    add_file_handler('error', logging.ERROR)
    add_file_handler('warning', logging.WARNING)

    # Thêm console handler để in log ra màn hình
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)  # Hiển thị mọi log từ mức DEBUG trở lên
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


class Logger:
    """Logger cho phép ghi log bất đồng bộ vào các tệp log và tệp cache."""

    cache = FileCache()  # Khởi tạo bộ nhớ cache để lưu trữ thông điệp log
    logger = setup_logger()

    @staticmethod
    async def __log__(
        message: str | Exception,
        write_cache: bool, level: str = "INFO"
    ) -> None:
        """Ghi log thông điệp ở mức đã chỉ định một cách bất đồng bộ."""
        level = level.lower()
        message = str(message) if isinstance(message, Exception) else message
        if write_cache:
            await Logger.cache.write(message, f'{level}.cache')
        await asyncio.to_thread(getattr(Logger.logger, level, Logger.logger.info), message)

    @staticmethod
    async def info(message: str | Exception, write_cache: bool = True):
        """Ghi một thông điệp info."""
        await Logger.__log__(message, write_cache, level="INFO")

    @staticmethod
    async def error(message: str | Exception, write_cache: bool = True):
        """Ghi một thông điệp lỗi."""
        await Logger.__log__(message, write_cache, level="ERROR")

    @staticmethod
    async def warning(message: str | Exception, write_cache: bool = True):
        """Ghi một thông điệp cảnh báo."""
        await Logger.__log__(message, write_cache, level="WARNING")

    @staticmethod
    async def debug(message: str | Exception, write_cache: bool = True):
        """Ghi một thông điệp debug."""
        await Logger.__log__(message, write_cache, level="DEBUG")