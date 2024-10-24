# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import logging

from sources.configs import file_paths
from sources.manager.files.filecache import FileCache



class AsyncLogger:
    cache = FileCache()

    @staticmethod
    async def notify_info(message: str | Exception):
        await AsyncLogger.cache.write(message, file_path='log-server.cache')

    @staticmethod
    async def notify_error(message: str | Exception):
        await AsyncLogger.cache.write(message, file_path='log-error.cache')


class Logger:
    """Logger cho phép ghi log vào file một cách bất đồng bộ."""

    def __init__(self, log_file: str):
        """Khởi tạo AsyncLogger."""
        self.log_file = file_paths(log_file)
        self.logger = None
        self.setup_logger()

    def setup_logger(self):
        """Thiết lập cấu hình cho logger."""
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

        # Thiết lập ghi log vào file
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    async def log(self, message: str, level: str = "INFO"):
        """Ghi log với mức độ đã chỉ định."""
        if level == "INFO":
            self.logger.info(message)
        elif level == "ERROR":
            self.logger.error(message)
        elif level == "WARNING":
            self.logger.warning(message)
        elif level == "DEBUG":
            self.logger.debug(message)
        else:
            self.logger.info(message)  # Mặc định ghi log ở mức độ INFO