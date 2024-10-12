# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import os
import typing
import asyncio
import aiosqlite
import threading

from . import settings


class DatabaseManager(settings.DatabaseManager):
    def __init__(self, db_path: str) -> None:
        self.cur = None
        self.conn = None
        self.lock = threading.Lock()
        self.db_path = db_path
        self.message_callback = None
        asyncio.run(self._initialize_database())

    async def _initialize_database(self):
        """Initialize the database and create tables if they do not exist."""
        if not os.path.exists(self.db_path):
            await self._create_tables()
            self._notify('Successfully created the database.')

    def _notify(self, message: str):
        """Notification method."""
        if self.message_callback:
            self.message_callback(f'Notify: {message}')

    def _notify_error(self, message: str):
        """Error notification method."""
        if self.message_callback:
            self.message_callback(f'Error: {message}')

    async def _create_tables(self) -> bool:
        """Create all necessary tables in the database."""
        with self.lock:  # Ensure thread safety
            try:
                await self._connection()  # Establish connection if not already
                async with self.conn:
                    await self.conn.executescript(''' 
                        CREATE TABLE IF NOT EXISTS account (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT NOT NULL UNIQUE,
                            password TEXT NOT NULL,
                            create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            ip_address TEXT
                        );
                        CREATE TABLE IF NOT EXISTS player (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            coin INTEGER DEFAULT 0,
                            appellation TEXT NOT NULL,
                            last_login_time TIMESTAMP DEFAULT '1979-12-31 11:01:01',
                            last_logout_time TIMESTAMP DEFAULT '1979-12-31 11:01:01',
                            ip_address TEXT
                        );
                        CREATE TABLE IF NOT EXISTS history (
                            id INTEGER NOT NULL,
                            action TEXT NOT NULL,
                            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            ip_address TEXT,
                            PRIMARY KEY (id, timestamp),
                            FOREIGN KEY (id) REFERENCES account (id) ON DELETE CASCADE
                        );
                    ''')
                self._notify("Tables created successfully.")
                return True  
            except aiosqlite.Error as e:
                self._notify_error(f"An error occurred while creating tables: {e}")
                return False

    async def _connection(self):
        """Establish a connection to the SQLite database."""
        try:
            self.conn = await aiosqlite.connect(database=self.db_path)
            self.cur = await self.conn.cursor()
        except aiosqlite.OperationalError as e:
            self._notify_error(e)

    async def _close(self):
        """Close the database connection."""
        if self.cur:
            await self.cur.close()
        if self.conn:
            await self.conn.close()

    def set_message_callback(self, callback):
        """Set a callback for messages."""
        self.message_callback = callback 

    async def execute_query(self, query: str, params: tuple = None) -> typing.Any:
        """Execute an SQL query."""
        if self.cur:
            try:
                await self.cur.execute(query, params or ())
                return await self.cur.fetchall()
            except Exception as e:
                self._notify_error(f"Query failed: {e} | Query: {query}")
                return None
        else:
            self._notify_error("Cursor is not initialized.")
            return None

    async def insert_account(self, username: str, password: str, ip_address: str) -> bool:
        """Insert a new account into the account table."""
        with self.lock:  # Ensure thread safety
            await self._connection()  # Establish connection if not already
            try:
                async with self.conn:  # Use a transaction context
                    await self.conn.execute('''INSERT INTO account (username, password, ip_address) VALUES (?, ?, ?)''', (username, password, ip_address))
                return True  # Indicate success
            except aiosqlite.IntegrityError:
                self._notify_error("Username already exists.")  # Notify error
                return False  # Indicate failure
            except aiosqlite.Error as e:
                self._notify_error(f"Failed to insert account: {e}")
                return False  # Indicate failure
            finally:
                await self._close()  # Close the connection

    async def insert_player(self, name: str, coin: int, appellation: str, ip_address: str) -> bool:
        """Insert a new player into the player table."""
        with self.lock:  # Ensure thread safety
            await self._connection()  # Establish connection if not already
            try:
                async with self.conn:
                    await self.conn.execute('''INSERT INTO player (name, coin, appellation, ip_address) VALUES (?, ?, ?, ?)''', (name, coin, appellation, ip_address))
                return True  # Indicate success
            except aiosqlite.Error as e:
                self._notify_error(f"Failed to insert player: {e}")
                return False  # Indicate failure
            finally:
                await self._close()  # Close the connection

    async def insert_history(self, id: int, action: str, ip_address: str) -> bool:
        """Insert a new history record."""
        with self.lock:  # Ensure thread safety
            await self._connection()  # Establish connection if not already
            try:
                async with self.conn:
                    await self.conn.execute('''INSERT INTO history (id, action, ip_address) VALUES (?, ?, ?)''', (id, action, ip_address))
                return True  # Indicate success
            except aiosqlite.Error as e:
                self._notify_error(f"Failed to insert history record: {e}")
                return False  # Indicate failure
            finally:
                await self._close()  # Close the connection

    async def get_player_history(self, id: int):
        """Query history records for a specific player."""
        with self.lock:
            await self._connection()
            history_records = await self.conn.execute('SELECT * FROM history WHERE id = ?', (id,))
            results = await history_records.fetchall()
            await self._close()  # Close the connection
            return results

    async def login(self, username: str, password: str) -> bool:
        """Check if the username and password match an account."""
        with self.lock:
            await self._connection()
            try:
                account = await self.conn.execute('SELECT * FROM account WHERE username = ? AND password = ?', (username, password))
                result = await account.fetchone()
                return result is not None  # Return True if account exists
            except aiosqlite.Error as e:
                self._notify_error(f"Login failed: {e}")
                return False
            finally:
                await self._close()

    async def register(self, username: str, password: str, ip_address: str) -> bool:
        """Register a new user account."""
        return await self.insert_account(username, password, ip_address)  # Reuse insert_account method

    async def get_account_data(self, username: str) -> typing.Optional[dict]:
        """Retrieve account data based on the username."""
        with self.lock:
            await self._connection()
            try:
                account = await self.conn.execute('SELECT * FROM account WHERE username = ?', (username,))
                result = await account.fetchone()
                if result:
                    return {
                        'id': result[0],
                        'username': result[1],
                        'create_time': result[3],
                        'update_time': result[4],
                        'ip_address': result[5]
                    }
                return None
            except aiosqlite.Error as e:
                self._notify_error(f"Failed to retrieve account data: {e}")
                return None
            finally:
                await self._close()
    
    async def get_player_coin(self, name: str) -> typing.Optional[int]:
        """Retrieve the coin amount of a specific player."""
        with self.lock:
            await self._connection()
            try:
                player = await self.conn.execute('SELECT coin FROM player WHERE name = ?', (name,))
                result = await player.fetchone()
                return result[0] if result else None  # Return coin amount or None if player not found
            except aiosqlite.Error as e:
                self._notify_error(f"Failed to retrieve player coin: {e}")
                return None
            finally:
                await self._close()
