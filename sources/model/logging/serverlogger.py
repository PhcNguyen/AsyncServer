# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

from sources.manager.files.filecache import FileCache



class AsyncLogger:
    cache = FileCache()

    @staticmethod
    async def notify(message: str | Exception):
        await AsyncLogger.cache.write(f'Notify: {message}')

    @staticmethod
    async def notify_error(message: str | Exception):
        await AsyncLogger.cache.write(f'Error: {message}')