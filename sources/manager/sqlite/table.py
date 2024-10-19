# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import aiosqlite

from sources import configs
from sources.utils import types
from sources.manager.files.iofiles import AsyncFileIO
from sources.utils.logger import AsyncLogger
from sources.manager.sqlite.utils import queries_line



class TableManager:
    def __init__(self, db_manager: types.DatabaseManager):
        self.db_manager = db_manager

    async def create_tables(self) -> bool:
        """Create necessary tables in the sqlite if they don't exist or are empty."""
        async with self.db_manager.lock:
            await AsyncLogger.notify("Checking for existing tables in the sqlite.")
            required_tables = ["account", "player"]
            existing_tables = await self._fetch_existing_tables()

            for table in required_tables:
                if table not in existing_tables or await self._is_table_empty(table):
                    await AsyncLogger.notify(f"Creating missing table: {table}.")
                    sql_commands = await AsyncFileIO.read_file(configs.file_paths('table.sql'))
                    if sql_commands:
                        await self._execute_sql_commands(sql_commands)
                        return True

            await AsyncLogger.notify("All required tables exist and are populated.")
            return True

    async def _fetch_existing_tables(self) -> set:
        """Fetch existing table names from the sqlite."""
        async with self.db_manager.conn.execute(await queries_line(2)) as cursor:
            return {row[0] for row in await cursor.fetchall()}

    async def _is_table_empty(self, table: str) -> bool:
        """Check if a specific table is empty."""
        async with self.db_manager.conn.execute(await queries_line(2)) as cursor:
            row = await cursor.fetchone()
            return row[0] == 0  # Return True if the table is empty

    async def _execute_sql_commands(self, sql_commands: str):
        """Execute SQL commands to create tables."""
        async with self.db_manager.lock:
            try:
                await AsyncLogger.notify(f"Executing SQL Commands: {sql_commands}")
                await self.db_manager.conn.executescript(sql_commands)
                await AsyncLogger.notify("Tables created successfully.")
            except aiosqlite.Error as e:
                await AsyncLogger.notify_error(f"Error creating tables: {e}")