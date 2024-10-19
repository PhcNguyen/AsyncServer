# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import asyncio
import aiosqlite

from sources import configs
from sources.utils.logger import AsyncLogger
from sources.manager.sql.tables import TableManager
from sources.manager.sql.player import PlayerManager
from sources.manager.sql.account import AccountManager



class SQLite:
    def __init__(self) -> None:
        self.conn = None
        self.lock = asyncio.Lock()
        self.db_type = 'sqlite'
        self.db_path = configs.file_paths('server.db')

        self.table = TableManager(self)
        self.account = AccountManager(self)
        self.player = PlayerManager(self)

    async def start(self):
        """Start the sqlite manager and initialize the sqlite connection."""
        try:
            if self.conn is None:
                self.conn = await aiosqlite.connect(self.db_path)
                await self.table.create_tables()
        except Exception as e:
            await AsyncLogger.notify_error(f"Lỗi kết nối đến cơ sở dữ liệu: {e}")

    async def close(self):
        """Close the sqlite connection."""
        if self.conn:
            await self.conn.close()
            await AsyncLogger.notify("Kết nối đã được đóng.")
            self.conn = None