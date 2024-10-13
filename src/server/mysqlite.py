import os
import asyncio
import aiosqlite
from typing import Any, Optional

from src.server.settings import DBSettings


class DBManager(DBSettings):
    def __init__(self, db_path: str) -> None:
        self.conn = None
        self.cur = None
        self.lock = asyncio.Lock()
        self.db_path = db_path
        self.message_callback = None
        asyncio.run(self._initialize_database())

    async def _initialize_database(self):
        """Initialize the database and create tables if they do not exist."""
        await self._connection()  # Ensure connection is established
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

    async def _connection(self):
        """Establish a connection to the SQLite database."""
        if not self.conn:
            try:
                self.conn = await aiosqlite.connect(self.db_path)
                self.cur = await self.conn.cursor()
                self._notify("Database connection established.")
            except aiosqlite.OperationalError as e:
                self._notify_error(f"Failed to connect to database: {e}")

    async def _close(self):
        """Close the database connection."""
        if self.cur:
            await self.cur.close()
        if self.conn:
            await self.conn.close()
        self.conn = None  # Set to None to indicate closed state

    async def _create_tables(self) -> bool:
        """Create all necessary tables in the database."""
        async with self.lock:  # Ensure thread safety using asyncio.Lock
            try:
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
    
    def set_message_callback(self, callback):
        """Set a callback for messages."""
        self.message_callback = callback 

    async def insert_account(self, username: str, password: str, ip_address: str) -> bool:
        """Insert a new account into the account table."""
        async with self.lock:
            try:
                async with self.conn:
                    await self.conn.execute('''
                        INSERT INTO account (username, password, ip_address) VALUES (?, ?, ?)
                    ''', (username, password, ip_address))
                    await self.conn.commit()  # Commit the transaction
                return True
            except aiosqlite.IntegrityError:
                self._notify_error("Username already exists.")
                return False
            except aiosqlite.Error as e:
                self._notify_error(f"Failed to insert account: {e}")
                return False

    async def login(self, username: str, password: str) -> bool:
        """Check if the username and password match an account."""
        async with self.lock:
            try:
                async with self.conn:
                    result = await self.conn.execute('''
                        SELECT * FROM account WHERE username = ? AND password = ?
                    ''', (username, password))
                    account = await result.fetchone()
                return account is not None  # Return True if account exists
            except aiosqlite.Error as e:
                self._notify_error(f"Login failed: {e}")
                return False

    async def get_player_coin(self, name: str) -> Optional[int]:
        """Retrieve the coin amount of a specific player."""
        async with self.lock:
            try:
                async with self.conn:
                    result = await self.conn.execute('''
                        SELECT coin FROM player WHERE name = ?
                    ''', (name,))
                    player = await result.fetchone()
                return player[0] if player else None
            except aiosqlite.Error as e:
                self._notify_error(f"Failed to retrieve player coin: {e}")
                return None