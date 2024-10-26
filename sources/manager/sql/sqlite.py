# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import asyncio
import aiosqlite

from sources import configs
from sources.utils.logger import AsyncLogger
from sources.manager.sql.tables import SQLTable
from sources.manager.sql.player import SQLPlayer
from sources.manager.sql.account import SQLAccount



class SQLite:
    def __init__(self) -> None:
        self.conn = None
        self.lock = asyncio.Lock()
        self.type = 'sqlite'
        self.config = configs.file_paths('server.db')
        self.create_table = False

        # Initialize managers
        self.table = SQLTable(self)
        self.player = SQLPlayer(self)
        self.account = SQLAccount(self)

    async def start(self) -> bool:
        """Start the SQLite manager and initialize the connection."""
        if self.conn is None:
            try:
                self.conn = await aiosqlite.connect(self.config)

                # Create tables if not created
                if not self.create_table:
                    if await self.table.create_tables():
                        self.create_table = True
                        return True
                    return False

                return True
            except aiosqlite.Error as e:
                self.conn = None
                await AsyncLogger.error(f"SQL: Error connecting to the database: {e}")
                return False
        else:
            await AsyncLogger.info("SQL: Connection already established.")
            return True

    async def close(self) -> None:
        """Close the SQLite connection."""
        if self.conn:
            await self.conn.close()
            await AsyncLogger.info("SQL: Connection closed.")
            self.conn = None
        else:
            await AsyncLogger.info("SQL: Connection already closed or not established.")