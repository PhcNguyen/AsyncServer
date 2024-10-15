# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

from sources.model.logging.cache import Cache



class ServerLogger:
    cache = Cache()

    @staticmethod
    def notify(message: str):
        ServerLogger.cache.write(f'Notify: {message}')

    @staticmethod
    def notify_error(message: str):
        ServerLogger.cache.write(f'Error: {message}')