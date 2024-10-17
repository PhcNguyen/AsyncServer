# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import asyncio
import aiosqlite

from sources import configs
from sources.manager.database.table import TableManager
from sources.manager.database.player import PlayerManager
from sources.manager.database.account import AccountManager



class DatabaseManager:
    def __init__(self) -> None:
        self.conn = None
        self.lock = asyncio.Lock()
        self.db_path = configs.file_paths('server.db')
        self.table_manager = TableManager(self)
        self.account_manager = AccountManager(self)
        self.player_manager = PlayerManager(self)

    async def start(self):
        """Start the database manager and initialize the database connection."""
        if self.conn is None:
            self.conn = await aiosqlite.connect(self.db_path)
            await self.table_manager.create_tables()

    async def close(self):
        """Close the database connection."""
        if self.conn:
            await self.conn.close()
            self.conn = None