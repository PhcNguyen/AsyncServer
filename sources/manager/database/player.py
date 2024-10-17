
import typing
import aiosqlite

from sources.model import types
from sources.model.logging import AsyncLogger
from sources.manager.database.utils import queries_line



class PlayerManager:
    def __init__(self, db_manager: types.DatabaseManager):
        self.db_manager = db_manager

    async def insert_player(self, **kwargs) -> bool:
        """Insert a new player into the player table using keyword arguments."""
        async with self.db_manager.lock:
            try:
                async with self.db_manager.conn:
                    await self.db_manager.conn.execute(
                        await queries_line(8),
                        (kwargs['name'], kwargs.get('coin', 0), kwargs['appellation'],
                         kwargs.get('last_login_time', '1979-12-31 11:01:01'),
                         kwargs.get('last_logout_time', '1979-12-31 11:01:01'))
                    )
                    await self.db_manager.conn.commit()
                return True
            except aiosqlite.Error as error:
                await AsyncLogger.notify_error(error)
                return False

    async def get_player_info(self, name: str) -> typing.Optional[dict]:
        """Retrieve all information of a specific player."""
        async with self.db_manager.lock:
            try:
                async with self.db_manager.conn:
                    result = await self.db_manager.conn.execute(await queries_line(3), (name,))
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