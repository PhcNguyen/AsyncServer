# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

from sources.configs import file_paths
from sources.utils.realtime import TimeUtil
from sources.manager.files.iofiles import FileIO
from sources.manager.files.filecache import FileCache



class AsyncLogger:
    cache = FileCache()

    @staticmethod
    async def notify(message: str | Exception):
        await AsyncLogger.cache.write(message, file_path='log-server.cache')
        '''
        await FileIO.write_file(
            file_paths(f"server.log"),
            f"{message}, {TimeUtil.now()}\n", "a"
        )
        '''

    @staticmethod
    async def notify_error(message: str | Exception):
        await AsyncLogger.cache.write(message, file_path='log-error.cache')
        await FileIO.write_file(
            file_paths(f"error.log"),
            f"{message}, {TimeUtil.now()}\n", "a"
        )