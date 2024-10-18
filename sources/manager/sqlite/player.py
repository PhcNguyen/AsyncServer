# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import aiosqlite

from sources.model import types, utils
from sources.manager.sqlite.utils import queries_line
from sources.model.logging import AsyncLogger



class PlayerManager:
    def __init__(self, db_manager: types.DatabaseManager):
        self.db_manager = db_manager

    async def dump_data(self, **kwargs) -> bool:
        """Insert a new player into the player table using keyword arguments."""
        async with self.db_manager.lock:
            try:
                async with self.db_manager.conn:
                    await self.db_manager.conn.execute(await queries_line(22), (kwargs['name'],))
                    await self.db_manager.conn.commit()
                return True
            except aiosqlite.Error as error:
                await AsyncLogger.notify_error(error)
                return False

    async def get(self, user_id: int) -> dict:
        """Retrieve all information of a specific player."""
        async with self.db_manager.lock:
            try:
                async with self.db_manager.conn:
                    result = await self.db_manager.conn.execute(await queries_line(3), (user_id,))
                    player = await result.fetchone()

                if player:
                    return utils.Response.success(
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

                return utils.Response.error(f"Người chơi với ID '{user_id}' không tồn tại.")
            except aiosqlite.Error as error:
                await AsyncLogger.notify_error(error)
                return utils.Response.error(f"Lỗi khi lấy thông tin người chơi với ID '{user_id}': {error}")

    async def update(self, user_id: int, **kwargs) -> dict:
        """Cập nhật thông tin của người chơi với ID đã cho."""
        async with self.db_manager.lock:
            try:
                async with self.db_manager.conn:
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

                    await self.db_manager.conn.execute(query, values)
                    await self.db_manager.conn.commit()

                return utils.Response.success("Thông tin người chơi đã được cập nhật thành công.")
            except aiosqlite.Error as error:
                await AsyncLogger.notify_error(error)
                return utils.Response.error(f"Lỗi khi cập nhật thông tin người chơi với ID '{user_id}': {error}")
