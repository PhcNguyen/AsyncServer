# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import os
import asyncio
import aiosqlite
import lib.bcrypt as bcrypt
from typing import Any, Optional

from src.model.settings import DBSettings
from src.realtime.time import formatted_time


class DBManager(DBSettings):
    def __init__(self, db_path: str) -> None:
        self.conn = None
        self.cur = None
        self.lock = asyncio.Lock()
        self.db_path = db_path
        self.message_callback = None
        asyncio.run(self._initialize_database())
    # ------------------------------- #
    # FUNCTION PRIVATE
    def _notify(self, message: str):
        """Notification method."""
        if self.message_callback:
            self.message_callback(f'Notify: {message}')

    def _notify_error(self, message: str):
        """Error notification method."""
        if self.message_callback:
            self.message_callback(f'Error: {message}')
    
    async def _initialize_database(self):
        """Initialize the database and create tables if they do not exist."""
        await self._connection()  # Ensure connection is established
        if not os.path.exists(self.db_path):
            await self._create_tables()
            self._notify('Successfully created the database.')

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
                            command TEXT NOT NULL,
                            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            ip_address TEXT,
                            PRIMARY KEY (id, timestamp),
                            FOREIGN KEY (id) REFERENCES account (id) ON DELETE CASCADE
                        );
                        CREATE TABLE IF NOT EXISTS history_transfer (
                            id INTEGER NOT NULL,
                            sender_name TEXT NOT NULL,
                            receiver_name TEXT NOT NULL,
                            amount INTEGER NOT NULL,
                            message TEXT,
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
    # ------------------------------- #
    # FUNCTION PUBLIC
    def set_message_callback(self, callback):
        """Set a callback for messages."""
        self.message_callback = callback 

    # INSERT DATA
    async def insert_account(self, username: str, password: str, ip_address: str) -> bool:
        """Register a new account in the account table."""
        # Check if the username already exists
        async with self.lock:
            try:
                password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                async with self.conn:
                    # Check if the username exists in the database
                    result = await self.conn.execute('''
                        SELECT * FROM account WHERE username = ?
                    ''', (username,))
                    account_exists = await result.fetchone()

                    if account_exists:
                        self._notify_error("Username already exists.")
                        return False  # Username already exists

                    # If the username does not exist, insert the new account
                    await self.conn.execute('''
                        INSERT INTO account (username, password, ip_address) VALUES (?, ?, ?)
                    ''', (username, password, ip_address))
                    await self.conn.commit()  # Commit the transaction

                    self._notify(f"[{username}]> Successfully registered.")
                    return True

            except aiosqlite.Error:
                self._notify_error(f"[{username}]> Failed to register.")
                return False
    
    async def insert_player(self, **kwargs) -> bool:
        """Insert a new player into the player table using keyword arguments."""
        name = kwargs.get('name')
        coin = kwargs.get('coin', 0)
        appellation = kwargs.get('appellation', '')
        last_login_time = kwargs.get('last_login_time', '1979-12-31 11:01:01')
        last_logout_time = kwargs.get('last_logout_time', '1979-12-31 11:01:01')
        ip_address = kwargs.get('ip_address', '')

        async with self.lock:
            try:
                async with self.conn:
                    await self.conn.execute('''
                        INSERT INTO player (
                            name, coin, appellation, 
                            last_login_time, last_logout_time, 
                            ip_address
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    ''', (name, coin, appellation, last_login_time, last_logout_time, ip_address))
                    await self.conn.commit()  # Commit the transaction
                return True
            except aiosqlite.Error as e:
                self._notify_error(f"[{name}]> Failed to insert player.")
                return False
                
    async def increase_player_coin(self, name: str, amount: int) -> bool:
        """Increase the coin amount of a specific player."""
        async with self.lock:
            try:
                async with self.conn:
                    # Cập nhật số tiền của người chơi
                    await self.conn.execute('''
                        UPDATE player SET coin = coin + ? WHERE name = ?
                    ''', (amount, name))
                    await self.conn.commit()  # Commit the transaction
                return True
            except aiosqlite.Error as e:
                self._notify_error(f"[{name}]> Failed to increase player coin.")
                return False
            
    # GET DATA
    async def login(self, username: str, password: str) -> bool:
        async with self.lock:
            try:
                async with self.conn:
                    result = await self.conn.execute(''' 
                        SELECT password FROM account WHERE username = ? 
                    ''', (username,))
                    account = await result.fetchone()

                if (account and bcrypt.checkpw(
                    password.encode('utf-8'), account[0])):
                    return True
                return False  # Tài khoản không hợp lệ
            except aiosqlite.Error as e:
                self._notify_error(f"Login failed: {e}")
                return False

    async def get_player_info(self, name: str) -> Optional[dict]:
        """Retrieve all information of a specific player."""
        async with self.lock:
            try:
                async with self.conn:
                    result = await self.conn.execute(''' 
                        SELECT * FROM player WHERE name = ? 
                    ''', (name,))
                    player_info = await result.fetchone()
                    
                if player_info:
                    # Convert the fetched data to a dictionary
                    return {
                        "id": player_info[0],
                        "name": player_info[1],
                        "coin": player_info[2],
                        "appellation": player_info[3],
                        "last_login_time": player_info[4],
                        "last_logout_time": player_info[5],
                        "ip_address": player_info[6]
                    }
                return None  # Return None if player not found
            except aiosqlite.Error as e:
                self._notify_error(f"Failed to retrieve player info: {e}")
                return None
    
    # UPDATE DATA
    async def update_player_appellation(self, name: str, new_appellation: str) -> bool:
        """Update the appellation of a specific player."""
        async with self.lock:
            try:
                async with self.conn:
                    # Cập nhật danh hiệu của người chơi
                    await self.conn.execute('''
                        UPDATE player SET appellation = ? WHERE name = ?
                    ''', (new_appellation, name))
                    await self.conn.commit()  # Commit the transaction
                return True
            except aiosqlite.Error as e:
                self._notify_error(f"Failed to update player appellation: {e}")
                return False
    
    async def update_player_coin(
        self, 
        name: str, 
        amount: int,
        player_id: int, 
        ip_address: str
    ) -> bool:
        """Increase/decrease the coin amount of a specific player."""
        async with self.lock:
            try:
                async with self.conn:
                    await self.conn.execute('''
                        UPDATE player SET coin = coin + ? WHERE name = ?
                    ''', (amount, name))
                    await self.conn.commit()  # Commit the transaction
                
                    result = await self.conn.execute(''' 
                            SELECT coin FROM player WHERE name = ? 
                        ''', (name,))
                    coins = await result.fetchone()
                    
                    sign = '+' if amount > 0 else ''
                    message = f"GD: {sign}{amount:,}COINS {formatted_time()}|SD: {coins[0]}COINS"

                    await self.log_transfer(
                        name, 'SERVER', amount,
                        message, player_id, ip_address
                    )

                return True
            except aiosqlite.Error as e:
                self._notify_error(f"Failed to increase player coin: {e}")
                return False
    
    async def transfer_coins(
        self, 
        sender_name: str, 
        receiver_name: str, 
        amount: int, 
        player_id: int, 
        ip_address: str
    ) -> bool:
        """Transfer coins from one player to another using the update_player_coin method."""
        async with self.lock:
            try:
                async with self.conn:
                    # Kiểm tra số dư của người gửi
                    result = await self.conn.execute(''' 
                        SELECT coin FROM player WHERE name = ? 
                    ''', (sender_name,))
                    sender_coins = await result.fetchone()

                    if not sender_coins or sender_coins[0] < amount:
                        self._notify_error(f"Insufficient funds in {sender_name}'s account.")
                        return False
                    
                    # Kiểm tra số dư của người nhận
                    result = await self.conn.execute(''' 
                        SELECT coin, id FROM player WHERE name = ? 
                    ''', (receiver_name,))
                    receiver = await result.fetchone()

                    message = f"GD: {{}}{amount:,}COINS {formatted_time()}|SD: {{}}COINS"

                    # Trừ tiền từ tài khoản người gửi
                    await self.update_player_coin(sender_name, -amount)
                    await self.log_transfer(
                        sender_name, receiver_name, amount,
                        message.format('-', sender_coins[0]), player_id, 
                        ip_address
                    )   
                    
                    # Thêm tiền vào tài khoản người nhận
                    await self.update_player_coin(receiver_name, amount)
                    await self.log_transfer(
                        receiver_name, sender_name, amount,
                        message.format('-', receiver[0]), receiver[1], ''
                    )
                
                return True
            except aiosqlite.Error as e:
                self._notify_error(f"Failed to transfer coins: {e}")
                return False
    # ------------------------------- # 
    # HISTORY
    async def log_action(self, id: int, command: str, ip_address: str = '') -> bool:
        """Log command to the history table."""
        async with self.lock:
            try:
                async with self.conn:
                    await self.conn.execute(''' 
                        INSERT INTO history (id, command, ip_address) 
                        VALUES (?, ?, ?)
                    ''', (id, command, ip_address))
                    await self.conn.commit()  # Commit the transaction
                return True
            except aiosqlite.Error as e:
                self._notify_error(f"Failed to log action: {e}")
                return False
        
    async def log_transfer(
        self, 
        sender_name: str, 
        receiver_name: str, 
        amount: int, 
        message:str, 
        player_id: int, 
        ip_address: str
    ) -> bool:
        """Log the transfer history for coins."""
        async with self.lock:
            try:
                async with self.conn:
                    await self.conn.execute(''' 
                        INSERT INTO history_transfer (
                            id, sender_name, receiver_name, 
                            amount, text, ip_address
                        ) 
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (player_id, sender_name, receiver_name, 
                          amount, message, ip_address
                        )
                    )
                    await self.conn.commit()  # Commit the transaction
                return True
            except aiosqlite.Error as e:
                self._notify_error(f"Failed to log transfer history: {e}")
                return False