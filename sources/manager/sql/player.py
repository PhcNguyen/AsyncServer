# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import aiosqlite

from sources.utils import types
from sources.constants.result import ResultBuilder
from sources.utils.sql import queries_line
from sources.utils.logger import AsyncLogger



class SQLPlayer:
    def __init__(self, database: types.SQLite | types.MySQL):
        """Initialize PlayerManager with the provided database."""
        self.database = database

    @staticmethod
    async def handle_error(message: str, error: Exception) -> dict:
        """Handle errors by logging and returning an error response."""
        await AsyncLogger.error(f"SQLITE: {error}")
        return ResultBuilder.error(message=message, error=error)

    @staticmethod
    def build_player_response(player: tuple) -> dict:
        """Build a structured response for player information."""
        return ResultBuilder.success(
            message="Thông tin người chơi đã được lấy thành công",
            id=player[0],
            name=player[1],
            coin=player[2],
            gem=player[3],
            power=player[4],
            hp=player[5],
            mp=player[6],
            damage=player[7],
            defense=player[8],
            crit=player[9],
            exp=player[10],
            character=player[11],
            description=player[12]
        )

    async def dump_data(self, **kwargs) -> bool:
        """Insert a new player into the player table using keyword arguments."""
        try:
            async with self.database.lock:
                await self.database.conn.execute(await queries_line(22), (kwargs['name'],))
                await self.database.conn.commit()
            return True
        except aiosqlite.Error as error:
            await self.handle_error("Lỗi khi thêm người chơi.", error)
            return False

    async def get(self, user_id: int) -> dict:
        """Retrieve all information of a specific player."""
        try:
            async with self.database.lock:
                result = await self.database.conn.execute(await queries_line(3), (user_id,))
                player = await result.fetchone()

            if player:
                return self.build_player_response(player)

            return ResultBuilder.error(message=f"Người chơi với ID '{user_id}' không tồn tại.")
        except aiosqlite.Error as error:
            return await self.handle_error(f"Lỗi khi lấy thông tin người chơi với ID '{user_id}'.", error)

    async def update(self, user_id: int, **kwargs) -> dict:
        """Update the player's information for the given user ID."""
        if not kwargs:
            return ResultBuilder.error(message="Không có thông tin nào để cập nhật.")

        try:
            async with self.database.lock:
                fields = ', '.join(f"{key} = ?" for key in kwargs.keys())
                values = list(kwargs.values()) + [user_id]

                query: str = await queries_line(3)
                query.replace('{fields}', ', '.join(fields))

                await self.database.conn.execute(query, values)
                await self.database.conn.commit()

            return ResultBuilder.success(message="Thông tin người chơi đã được cập nhật thành công.")
        except aiosqlite.Error as error:
            return await self.handle_error(f"Lỗi khi cập nhật thông tin người chơi với ID '{user_id}'.", error)