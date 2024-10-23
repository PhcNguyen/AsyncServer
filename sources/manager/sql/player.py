# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import aiosqlite

from sources.utils import types
from sources.utils.response import ResponseBuilder
from sources.utils.sqlite import queries_line
from sources.utils.logger import AsyncLogger



class PlayerManager:
    def __init__(self, database: types.SQLite | types.MySQL):
        self.database = database

    async def dump_data(self, **kwargs) -> bool:
        """Insert a new player into the player table using keyword arguments."""
        async with self.database.lock:
            try:
                async with self.database.conn:
                    await self.database.conn.execute(await queries_line(22), (kwargs['name'],))
                    await self.database.conn.commit()
                return True
            except aiosqlite.Error as error:
                await AsyncLogger.notify_error(f"SQLITE: {error}")
                return False

    async def get(self, user_id: int) -> dict:
        """Retrieve all information of a specific player."""
        async with self.database.lock:
            try:
                async with self.database.conn:
                    result = await self.database.conn.execute(await queries_line(3), (user_id,))
                    player = await result.fetchone()

                if player:
                    return ResponseBuilder.success(
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

                return ResponseBuilder.error(message=f"Người chơi với ID '{user_id}' không tồn tại.")
            except aiosqlite.Error as error:
                await AsyncLogger.notify_error(f"SQLITE: {error}")
                return ResponseBuilder.error(message=f"Lỗi khi lấy thông tin người chơi với ID '{user_id}': {error}")

    async def update(self, user_id: int, **kwargs) -> dict:
        """Cập nhật thông tin của người chơi với ID đã cho."""
        async with self.database.lock:
            try:
                async with self.database.conn:
                    # Tạo danh sách các trường cần cập nhật và giá trị của chúng
                    fields = []
                    values = []

                    for key, value in kwargs.items():
                        fields.append(f"{key} = ?")
                        values.append(value)

                    # Thêm user_id vào cuối danh sách giá trị
                    values.append(user_id)

                    # Thực hiện câu lệnh SQL để cập nhật
                    query: str = await queries_line(3)
                    query.replace('{fields}', ', '.join(fields))

                    await self.database.conn.execute(query, values)
                    await self.database.conn.commit()

                return ResponseBuilder.success(message="Thông tin người chơi đã được cập nhật thành công.")
            except aiosqlite.Error as error:
                await AsyncLogger.notify_error(f"SQLITE: {error}")
                return ResponseBuilder.error(message=f"Lỗi khi cập nhật thông tin người chơi với ID '{user_id}': {error}")