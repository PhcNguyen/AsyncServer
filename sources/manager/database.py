# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import typing
import bcrypt
import asyncio
import aiofiles 
import aiosqlite

from sources.application.configs import Configs
from sources.model.realtime import Realtime



class DBManager(Configs.DirPath):
    def __init__(self) -> None:
        self.conn = None
        self.cur = None
        self.lock = asyncio.Lock()
        self.db_path = DBManager.db_path
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
    
    async def _read_sql_file(self, path: str) -> str:
        """Read SQL commands from a file asynchronously."""
        try:
            async with aiofiles.open(
                path, mode='r', 
                encoding='utf-8', errors='ignore'
            ) as file:
                return await file.read()
        except Exception as error:
            self._notify_error(error)
            return ""
    
    async def _initialize_database(self):
        """Initialize the database and create tables if they do not exist."""
        if self.conn is None:
            self.conn = await aiosqlite.connect(self.db_path)  # Establish the connection
        await self._create_tables()
        
    async def _connection(self):
        """Establish a connection to the SQLite database."""
        if not self.conn:
            try:
                self.conn = await aiosqlite.connect(self.db_path)
                self.cur = await self.conn.cursor()
            except aiosqlite.OperationalError as error:
                self._notify_error(error)

    async def _create_tables(self) -> bool:
        """Create all necessary tables in the database."""
        sql_commands = await self._read_sql_file(DBManager.table_path)
        if not sql_commands:
            return False  # Exit if no SQL commands are found

        async with self.lock:  # Ensure thread safety using asyncio.Lock
            try:
                # Use the connection directly, ensuring it is initialized
                await self.conn.executescript(sql_commands)
                self._notify("Tables created successfully.")
                return True  
            except aiosqlite.Error as e:
                self._notify_error(f"An error occurred while creating tables: {e}")
                return False
            
    async def _queries_line(self, line_number: int):
        try:
            async with aiofiles.open(self.queries_path, mode='r') as file:
                lines = await file.readlines()  # Đọc tất cả các dòng
                # Loại bỏ các dòng trống và dòng bắt đầu bằng "--"
                valid_lines = [line.strip() for line in lines if line.strip() and not line.strip().startswith('--')]
                
                # Kiểm tra xem dòng yêu cầu có nằm trong phạm vi hợp lệ không
                if 1 <= line_number <= len(valid_lines): 
                    return valid_lines[line_number - 1]  # Trả về dòng yêu cầu
                return None
        except Exception as error:
            self._notify_error(error)
            return None
        
    # ------------------------------- #
    # FUNCTION PUBLIC
    def set_message_callback(self, callback):
        """Set a callback for messages."""
        self.message_callback = callback 

    async def close(self):
        """Close the database connection."""
        if self.cur:
            await self.cur.close()
        if self.conn:
            await self.conn.close()
        self.conn = None  # Set to None to indicate closed state

    # ------------------------------- #
    # INSERT DATA
    async def insert_account(self, username: str, password: str) -> bool:
        """Register a new account in the account table."""
        # Check if the username already exists
        async with self.lock:
            try:
                password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                async with self.conn:
                    # Check if the username exists in the database
                    result = await self.conn.execute(await self._queries_line(1), (username,))
                    account_exists = await result.fetchone()

                    if account_exists:
                        self._notify_error("Username already exists.")
                        return False  # Username already exists

                    # If the username does not exist, insert the new account
                    await self.conn.execute(await self._queries_line(7), (username, password))
                    await self.conn.commit()  # Commit the transaction

                    return True
            except aiosqlite.Error as error:
                self._notify_error(error)
                return False
    
    async def insert_player(self, **kwargs) -> bool:
        """Insert a new player into the player table using keyword arguments."""
        name = kwargs.get('name')
        coin = kwargs.get('coin', 0)
        appellation = kwargs.get('appellation', '')
        last_login_time = kwargs.get('last_login_time', '1979-12-31 11:01:01')
        last_logout_time = kwargs.get('last_logout_time', '1979-12-31 11:01:01')

        async with self.lock:
            try:
                async with self.conn:
                    await self.conn.execute(
                        await self._queries_line(8), 
                        (name, coin, appellation, last_login_time, last_logout_time)
                    )
                    await self.conn.commit()  # Commit the transaction
                return True
            except aiosqlite.Error as error:
                self._notify_error(error)
                return False
                
    async def increase_player_coin(self, name: str, amount: int) -> bool:
        """Increase the coin amount of a specific player."""
        async with self.lock:
            try:
                async with self.conn:
                    # Cập nhật số tiền của người chơi
                    await self.conn.execute(await self._queries_line(14), (amount, name))
                    await self.conn.commit()  # Commit the transaction
                return True
            except aiosqlite.Error as error:
                self._notify_error(error)
                return False
    
    # ------------------------------- #
    # GET DATA
    async def login(self, username: str, password: str) -> bool:
        async with self.lock:
            try:
                async with self.conn:
                    result = await self.conn.execute(await self._queries_line(2), (username,))
                    account = await result.fetchone()

                if (account and bcrypt.checkpw(
                    password.encode('utf-8'), account[0])):
                    return True
                return False  # Tài khoản không hợp lệ
            except aiosqlite.Error as error:
                self._notify_error(error)
                return False

    async def get_player_info(self, name: str) -> typing.Optional[dict]:
        """Retrieve all information of a specific player."""
        async with self.lock:
            try:
                async with self.conn:
                    result = await self.conn.execute(await self._queries_line(3), (name,))
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
            except aiosqlite.Error as error:
                self._notify_error(error)
                return None
            
    # ------------------------------- #
    # UPDATE DATA
    async def update_player_appellation(self, name: str, new_appellation: str) -> bool:
        """Update the appellation of a specific player."""
        async with self.lock:
            try:
                async with self.conn:
                    # Cập nhật danh hiệu của người chơi
                    await self.conn.execute(await self._queries_line(15), (new_appellation, name))
                    await self.conn.commit()  # Commit the transaction
                return True
            except aiosqlite.Error as error:
                self._notify_error(error)
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
                    await self.conn.execute(await self._queries_line(14), (amount, name))
                    await self.conn.commit()  # Commit the transaction
                
                    result = await self.conn.execute(await self._queries_line(14), (name,))
                    coins = await result.fetchone()
                    
                    sign = '+' if amount > 0 else ''
                    message = "GD: {}{:,}COINS {}|SD: {}COINS".format(
                        sign, amount, 
                        Realtime.formatted_time(), coins[0]
                    )

                    await self.log_transfer(
                        name, 'SERVER', amount,
                        message, player_id, ip_address
                    )

                return True
            except aiosqlite.Error as error:
                self._notify_error(error)
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
                    result = await self.conn.execute(await self._queries_line(4), (sender_name,))
                    sender_coins = await result.fetchone()

                    if not sender_coins or sender_coins[0] < amount:
                        self._notify_error(f"Insufficient funds in {sender_name}'s account.")
                        return False
                    
                    # Kiểm tra số dư của người nhận
                    result = await self.conn.execute(await self._queries_line(4), (receiver_name,))
                    receiver = await result.fetchone()

                    message = f"GD: {{}}{amount:,}COINS {Realtime.formatted_time()}|SD: {{}}COINS"

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
            except aiosqlite.Error as error:
                self._notify_error(error)
                return False
            
    # ------------------------------- # 
    # HISTORY
    async def log_action(self, id: int, command: str, ip_address: str = '') -> bool:
        """Log command to the history table."""
        async with self.lock:
            try:
                async with self.conn:
                    await self.conn.execute(await self._queries_line(9), (id, command, ip_address))
                    await self.conn.commit()  # Commit the transaction
                return True
            except aiosqlite.Error as error:
                self._notify_error(error)
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
                    await self.conn.execute(
                        await self._queries_line(10), 
                        (
                            player_id, sender_name, receiver_name, 
                            amount, message, ip_address
                        )
                    )
                    await self.conn.commit()  # Commit the transaction
                return True
            except aiosqlite.Error as error:
                self._notify_error(error)
                return False