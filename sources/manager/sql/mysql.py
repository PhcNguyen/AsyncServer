# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import asyncio
import aiomysql

from sources import configs
from sources.utils.logger import AsyncLogger
from sources.manager.sql.player import PlayerManager
from sources.manager.sql.account import AccountManager



class MySQL:
    def __init__(self) -> None:
        self.conn = None
        self.lock = asyncio.Lock()
        self.type = 'mysql'
        self.config = configs.load_database("mysql.xml")
        self.ip = f"('{self.config['host']}', {self.config['port']})"

        self.player = PlayerManager(self)
        self.account = AccountManager(self)

    async def start(self) -> bool:
        """Start the MySQL manager and initialize the MySQL connection."""
        if self.conn is None:
            try:

                self.conn = await aiomysql.connect(**self.config)
                await AsyncLogger.notify(f"Connection MySQL established at {self.ip}")
                return True
            except aiomysql.Error as e:
                self.conn = None
                await AsyncLogger.notify_error(f"Lỗi kết nối đến cơ sở dữ liệu: {e}")
                return False
        else:
            await AsyncLogger.notify(f"MySQL đạ được kết nối tại {self.ip}")
            return True

    async def close(self) -> bool:
        """Close the MySQL connection."""
        if self.conn:
            self.conn.close()
            await AsyncLogger.notify("Kết nối đã được đóng.")
            self.conn = None
            return True
        else:
            await AsyncLogger.notify("Kết nối MySQL đã được đóng trước đó hoặc chưa được thiết lập.")
            return False