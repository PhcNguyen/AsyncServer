# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import logging
import asyncio

from sources.configs import file_paths
from sources.manager.files.filecache import FileCache



class AsyncLogger:
    cache = FileCache()

    @staticmethod
    async def info(message: str | Exception):
        await AsyncLogger._log(message, 'log-server.cache')

    @staticmethod
    async def error(message: str | Exception):
        await AsyncLogger._log(message, 'log-error.cache')

    @staticmethod
    async def warning(message: str | Exception):
        await AsyncLogger._log(message, 'log-warning.cache')

    @staticmethod
    async def _log(message: str | Exception, file_path: str):
        """Ghi nhật ký thông điệp vào tệp cache tương ứng."""
        if isinstance(message, Exception):
            message = f"Error occurred: {str(message)}"  # Chuyển đổi Exception thành chuỗi
        await AsyncLogger.cache.write(message, file_path=file_path)



class Logger:
    """Logger that allows asynchronous logging to a file."""

    def __init__(self, log_file: str):
        """Initialize the logger."""
        self.logger = None
        self.log_file = file_paths(log_file)
        self.setup_logger()

    def setup_logger(self):
        """Set up logger configuration."""
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

        # Set up logging to file with UTF-8 encoding
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')  # Set encoding to 'utf-8'
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    async def log(self, message: str, level: str = "INFO"):
        """Log the message at the specified level asynchronously."""
        log_methods = {
            "INFO": self.logger.info,
            "ERROR": self.logger.error,
            "WARNING": self.logger.warning,
            "DEBUG": self.logger.debug
        }

        log_method = log_methods.get(level.upper(), self.logger.info)

        # Execute the logging method asynchronously
        await asyncio.to_thread(log_method, message)