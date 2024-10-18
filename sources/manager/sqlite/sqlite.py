# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import asyncio
import aiosqlite

from sources import configs
from sources.manager.sqlite.table import TableManager
from sources.manager.sqlite.player import PlayerManager
from sources.manager.sqlite.account import AccountManager



class DatabaseManager:
    def __init__(self) -> None:
        self.conn = None
        self.lock = asyncio.Lock()
        self.db_path = configs.file_paths('server.db')

        self.table = TableManager(self)
        self.account = AccountManager(self)
        self.player = PlayerManager(self)

    async def start(self):
        """Start the sqlite manager and initialize the sqlite connection."""
        if self.conn is None:
            self.conn = await aiosqlite.connect(self.db_path)
            await self.table.create_tables()

    async def close(self):
        """Close the sqlite connection."""
        if self.conn:
            await self.conn.close()
            self.conn = None