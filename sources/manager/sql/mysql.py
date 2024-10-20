
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
        self.type = 'mysql'
        self.config = configs.load_database("mysql.xml")

        self.player = PlayerManager(self)
        self.account = AccountManager(self)

    async def start(self):
        """Start the MySQL manager and initialize the MySQL connection."""
        if self.conn is None:
            try:
                self.conn = await aiomysql.connect(**self.config)
                await AsyncLogger.notify(
                    f"Connection MySQL established at ('{self.config['host']}', {self.config['port']})")
            except aiomysql.Error as e:
                await AsyncLogger.notify_error(f"Lỗi kết nối đến cơ sở dữ liệu: {e}")
                self.conn = None  # Đảm bảo rằng self.conn là None khi kết nối không thành công
        else:
            await AsyncLogger.notify("Kết nối MySQL đã được thiết lập.")

    async def close(self):
        """Close the MySQL connection."""
        if self.conn:
            await self.conn.close()
            await AsyncLogger.notify("Kết nối đã được đóng.")
            self.conn = None
        else:
            await AsyncLogger.notify("Kết nối MySQL đã được đóng trước đó hoặc chưa được thiết lập.")