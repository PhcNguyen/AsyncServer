
import asyncio
import aiomysql

from sources import configs
from sources.utils.logger import AsyncLogger
from sources.manager.sql.tables import TableManager
from sources.manager.sql.player import PlayerManager
from sources.manager.sql.account import AccountManager



class MySQL:
    def __init__(self) -> None:
        self.conn = None
        self.lock = asyncio.Lock()
        self.db_type = 'mysql'
        self.db_config = configs.load_database("mysql.xml")

        self.table = TableManager(self)
        self.account = AccountManager(self)
        self.player = PlayerManager(self)

    async def start(self):
        """Start the MySQL manager and initialize the MySQL connection."""
        if self.conn is None:
            try:
                self.conn = await aiomysql.connect(**self.db_config)
                await self.table.create_tables()
            except aiomysql.Error as e:
                await AsyncLogger.notify_error(f"Lỗi kết nối đến cơ sở dữ liệu: {e}")

    async def close(self):
        """Close the MySQL connection."""
        if self.conn:
            await self.conn.close()
            await AsyncLogger.notify("Kết nối đã được đóng.")
            self.conn = None
