# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import typing
import bcrypt
import asyncio
import aiofiles
import aiosqlite

from sources.manager import iofiles
from sources.model.realtime import Realtime
from sources.application.configs import Configs
from sources.model.logging.serverlogger import AsyncLogger


class DatabaseManager:
    def __init__(self) -> None:
        self.conn = None
        self.lock = asyncio.Lock()

        # Database and file paths from the configuration
        self.db_path = Configs.FILE_PATHS['server.db']
        self.table_path = Configs.FILE_PATHS['table.sql']
        self.queries_path = Configs.FILE_PATHS['queries.sql']

        # Initialize the database
        asyncio.run(self._initialize_database())

    async def _initialize_database(self):
        """Initialize the database and create tables if they do not exist."""
        if self.conn is None:
            self.conn = await aiosqlite.connect(self.db_path)

        await self._create_tables()

    async def _create_tables(self) -> bool:
        """Create all necessary tables in the database if they don't exist or are empty."""
        async with self.lock:
            await AsyncLogger.notify("Checking for existing tables in the database.")

            required_tables = ["account", "player"]
            existing_tables = await self._fetch_existing_tables()

            # Create missing tables or notify if data already exists
            for table in required_tables:
                if table not in existing_tables:
                    await AsyncLogger.notify(f"Missing table: {table}. Proceeding to create tables.")
                    break
                if await self._is_table_empty():
                    await AsyncLogger.notify(f"Table {table} is empty. Proceeding to create tables.")
                    break
            else:
                await AsyncLogger.notify("Data already exists in the database.")
                return True  # If data exists, no need to create tables

            sql_commands = await iofiles.read_files(self.table_path)
            if not sql_commands:
                await AsyncLogger.notify_error("No SQL commands found to create tables.")
                return False

            await self._execute_sql_commands(sql_commands)
            return True

    async def _fetch_existing_tables(self) -> set:
        """Fetch existing table names from the database."""
        async with self.conn.execute(await self._queries_line(20)) as cursor:
            return {row[0] for row in await cursor.fetchall()}

    async def _is_table_empty(self) -> bool:
        """Check if a specific table is empty."""
        async with self.conn.execute(await self._queries_line(20)) as cursor:
            row = await cursor.fetchone()
            return row[0] == 0  # Return True if the table is empty

    async def _execute_sql_commands(self, sql_commands: str):
        """Execute SQL commands to create tables."""
        async with self.lock:
            try:
                await AsyncLogger.notify(f"Executing SQL Commands: {sql_commands}")
                await self.conn.executescript(sql_commands)
                await AsyncLogger.notify("Tables created successfully.")
            except aiosqlite.Error as e:
                await AsyncLogger.notify_error(f"An error occurred while creating tables: {e}")

    async def _queries_line(self, line_number: int):
        try:
            # Đọc toàn bộ nội dung của tệp
            content = await iofiles.read_files(self.queries_path, mode='r')

            valid_lines = [line.strip() for line in content.split(';') if line.strip()]

            if valid_lines:
                if 1 <= line_number <= len(valid_lines):
                    query = valid_lines[line_number - 1].strip() + ';'  # Thêm dấu chấm phẩy vào cuối câu lệnh
                    return query
                await AsyncLogger.notify_error(f"Invalid line number: {line_number}")
                return None
            else:
                await AsyncLogger.notify_error("No valid lines found in the file.")
                return None
        except Exception as error:
            await AsyncLogger.notify_error(error)
            return None

    async def close(self):
        """Close the database connection."""
        if self.conn:
            await self.conn.close()
            self.conn = None

    async def insert_account(self, username: str, password: str) -> bool:
        """Register a new account in the account table."""
        async with self.lock:
            try:
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                async with self.conn:
                    account_exists = await self._account_exists(username)

                    if account_exists:
                        await AsyncLogger.notify_error(f"Username '{username}' already exists.")
                        return False  # Username already exists

                    await self.conn.execute(await self._queries_line(7), (username, hashed_password))
                    await self.conn.commit()

                await AsyncLogger.notify(f"Account '{username}' created successfully.")
                return True
            except aiosqlite.Error as error:
                await AsyncLogger.notify_error(f"Error creating account '{username}': {error}")
                return False

    async def _account_exists(self, username: str) -> bool:
        """Check if an account with the given username exists."""
        result = await self.conn.execute(await self._queries_line(1), (username,))
        account_exists = await result.fetchone()
        return account_exists is not None

    async def insert_player(self, **kwargs) -> bool:
        """Insert a new player into the player table using keyword arguments."""
        async with self.lock:
            try:
                async with self.conn:
                    await self.conn.execute(
                        await self._queries_line(8),
                        (kwargs['name'], kwargs.get('coin', 0), kwargs['appellation'],
                         kwargs.get('last_login_time', '1979-12-31 11:01:01'),
                         kwargs.get('last_logout_time', '1979-12-31 11:01:01'))
                    )
                    await self.conn.commit()
                return True
            except aiosqlite.Error as error:
                await AsyncLogger.notify_error(error)
                return False

    async def increase_player_coin(self, name: str, amount: int) -> bool:
        """Increase the coin amount of a specific player."""
        async with self.lock:
            try:
                async with self.conn:
                    await self.conn.execute(await self._queries_line(14), (amount, name))
                    await self.conn.commit()
                return True
            except aiosqlite.Error as error:
                await AsyncLogger.notify_error(error)
                return False

    async def login(self, username: str, password: str) -> bool:
        """Verify user's credentials for login."""
        async with self.lock:
            try:
                async with self.conn:
                    result = await self.conn.execute(await self._queries_line(2), (username,))
                    account = await result.fetchone()

                if account and bcrypt.checkpw(password.encode('utf-8'), account[0]):
                    return True
                return False  # Invalid credentials
            except aiosqlite.Error as error:
                await AsyncLogger.notify_error(error)
                return False

    async def get_player_info(self, name: str) -> typing.Optional[dict]:
        """Retrieve all information of a specific player."""
        async with self.lock:
            try:
                async with self.conn:
                    result = await self.conn.execute(await self._queries_line(3), (name,))
                    player_info = await result.fetchone()

                if player_info:
                    return {
                        "id": player_info[0],
                        "name": player_info[1],
                        "coin": player_info[2],
                        "appellation": player_info[3],
                        "last_login_time": player_info[4],
                        "last_logout_time": player_info[5],
                    }
                return None  # Player not found
            except aiosqlite.Error as error:
                await AsyncLogger.notify_error(error)
                return None

    async def update_player_appellation(self, name: str, new_appellation: str) -> bool:
        """Update the appellation of a specific player."""
        async with self.lock:
            try:
                async with self.conn:
                    await self.conn.execute(await self._queries_line(15), (new_appellation, name))
                    await self.conn.commit()
                return True
            except aiosqlite.Error as error:
                await AsyncLogger.notify_error(error)
                return False

    async def update_player_coin(self, name: str, amount: int, account_id: int) -> bool:
        """Increase/decrease the coin amount of a specific player."""
        async with self.lock:
            try:
                async with self.conn:
                    await self.conn.execute(await self._queries_line(14), (amount, name))
                    await self.conn.commit()

                    result = await self.conn.execute(await self._queries_line(14), (name,))
                    coins = await result.fetchone()

                    sign = '+' if amount > 0 else ''
                    message = "GD: {}{:,}COINS {}|SD: {}COINS".format(
                        sign, amount, Realtime.formatted_time(), coins[0]
                    )

                    await self.log_transfer(name, 'SERVER', amount, message, account_id)

                return True
            except aiosqlite.Error as error:
                await AsyncLogger.notify_error(error)
                return False

    async def transfer_coins(self, sender_name: str, receiver_name: str, amount: int, account_id: int) -> bool:
        """Transfer coins from one player to another."""
        async with self.lock:
            try:
                async with self.conn:
                    # Check sender's balance
                    sender_coins = await self._get_player_balance(sender_name)
                    if sender_coins < amount:
                        await AsyncLogger.notify_error(f"Insufficient funds in {sender_name}'s account.")
                        return False

                    # Transfer coins
                    await self.update_player_coin(sender_name, -amount, account_id)
                    await self.update_player_coin(receiver_name, amount, account_id)

                    # Log the transfers
                    await self.log_transfer(sender_name, receiver_name, amount, f"Transfer: -{amount:,}COINS", account_id)
                    await self.log_transfer(receiver_name, sender_name, amount, f"Transfer: +{amount:,}COINS", account_id)

                return True
            except aiosqlite.Error as error:
                await AsyncLogger.notify_error(error)
                return False

    async def _get_player_balance(self, name: str) -> int:
        """Get the current balance of a player."""
        async with self.conn:
            result = await self.conn.execute(await self._queries_line(14), (name,))
            balance = await result.fetchone()
            return balance[0] if balance else 0  # Return balance or 0 if player not found

    @staticmethod
    async def log_transfer(player: str, to: str, amount: int, message: str, account_id: int) -> None:
        """Log the coin transfer action."""
        await AsyncLogger.notify(f"({account_id},{player}) transferred {amount} coins to {to}: {message}")