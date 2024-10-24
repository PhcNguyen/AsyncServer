# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import aiomysql
import aiosqlite

from sources import configs
from sources.utils import types
from sources.manager.files.iofiles import FileIO
from sources.utils.logger import AsyncLogger
from sources.utils.sql import queries_line



class TableManager:
    REQUIRED_TABLES = [
        "account", "player", "player_bag",
        "clan", "mob", "store", "item",
        "itemsell", "event", "history"
    ]

    def __init__(self, database: types.SQLite | types.MySQL):
        self.database = database

    async def create_tables(self) -> bool:
        """Create necessary tables in the sqlite if they don't exist or are empty."""
        async with self.database.lock:
            await AsyncLogger.notify_info(f"SQL: Kiểm tra các bảng hiện có trong {self.database.type}")
            existing_tables = await self._fetch_existing_tables()

            tables_to_create = []
            for table in TableManager.REQUIRED_TABLES:
                if table not in existing_tables or await self._is_table_empty(table):
                    tables_to_create.append(table)

            if tables_to_create:
                await AsyncLogger.notify_info(f"SQL: Tạo bảng bị thiếu: {', '.join(tables_to_create)}")
                sql_commands = await FileIO.read_file(configs.file_paths('create.sql'))
                if sql_commands:
                    await self._execute_sql_commands(sql_commands)
                    return True

            await AsyncLogger.notify_info("SQL: Tất cả các bảng bắt buộc đã tồn tại")
            return True

    async def _fetch_existing_tables(self) -> set:
        """Fetch existing table names from the sqlite."""
        try:
            async with self.database.conn.execute(await queries_line(2)) as cursor:
                return {row[0] for row in await cursor.fetchall()}
        except aiosqlite.Error as e:
            await AsyncLogger.notify_error(f"SQL: Lỗi tìm nạp bảng hiện có: {e}")
            return set()  # Return empty set in case of error

    async def _is_table_empty(self, table: str) -> bool:
        """Kiểm tra xem bảng có trống hay không."""
        try:
            async with self.database.conn.execute(await queries_line(2)) as cursor:
                row = await cursor.fetchone()
                return row[0] == 0  # Trả về True nếu bảng trống
        except (aiosqlite.Error, aiomysql.Error) as e:
            await AsyncLogger.notify_error(f"SQL: Lỗi kiểm tra xem bảng {table} có trống rỗng: {e}")
            return True  # Giả định bảng trống nếu có lỗi

    async def _execute_sql_commands(self, sql_commands: str):
        """Execute SQL commands to create tables."""
        try:
            await self.database.conn.executescript(sql_commands)
            await self.database.conn.commit()
            await AsyncLogger.notify_info("SQL: Bảng được tạo thành công")
        except aiosqlite.Error as e:
            await AsyncLogger.notify_error(f"SQL: Lỗi khi tạo bảng: {e}")

    async def list_tables(self):
        try:
            cursor = await self.database.conn.execute(await queries_line(2))
            tables = await cursor.fetchall()
            await AsyncLogger.notify_info(f"SQL: Các bảng hiện có: {tables}")
        except aiosqlite.Error as e:
            await AsyncLogger.notify_error(f"SQL: Lỗi khi liệt kê các bảng: {e}")