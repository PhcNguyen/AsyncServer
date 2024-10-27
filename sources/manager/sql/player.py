# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import aiosqlite

from sources.utils import types
from sources.utils.logger import Logger
from sources.manager.sql.utils import queries_line



class SQLPlayer:
    def __init__(self, database: types.SQLite | types.MySQL):
        """Initialize PlayerManager with the provided database."""
        self.database = database

    async def dump_data(self, **kwargs) -> bool:
        """Insert a new player into the player table using keyword arguments."""
        try:
            async with self.database.lock:
                await self.database.conn.execute(await queries_line(22), (kwargs['name'],))
                await self.database.conn.commit()
            return True
        except aiosqlite.Error as error:
            await Logger.error(f"SQL: {error}", False)
            return False

    async def get(self, user_id: int) -> dict | bool:
        """
        Retrieve all information of a specific player.

        [0] ID của người chơi - [1] Tên người chơi
        [2] Số tiền (coin) của người chơi
        [3] Số gem (đá quý) của người chơi
        [4] Máu (HP) của người chơi
        [5] Năng lượng (MP) của người chơi
        [6] Tốc độ của người chơi
        [7] Sát thương của người chơi
        [8] Phòng thủ của người chơi
        [9] Tỉ lệ chí mạng của người chơi

        [10] Sức mạnh tổng thể của người chơi
        [11] Kinh nghiệm (EXP) của người chơi
        [12] Vị trí hiện tại của người chơi
        [13] Trang bị trên cơ thể của người chơi
        [14] Đồ trong túi (bag) của người chơi
        [15] Đồ trong hộp (box) của người chơi
        [16] Danh sách bạn bè của người chơi
        [17] Dữ liệu nhiệm vụ của người chơi
        [18] Sức chứa tối đa (luggage) của người chơi
        [19] Cấp độ của túi đồ (bag level)
        [20] ID của bang hội (clan) của người chơi
        [21] Mô tả về người chơi
        """
        try:
            async with self.database.lock:
                result = await self.database.conn.execute(await queries_line(3), (user_id,))
                data = await result.fetchone()

            if data: return data

            await Logger.error(f"ID {user_id} không tồn tại")
            return False
        except aiosqlite.Error as error:
            await Logger.error(f"ID: {user_id} - SQL: {error}", False)
            return False

    async def update(self, user_id: int, **kwargs) -> bool:
        """Update the player's information for the given user ID."""
        if not kwargs:
            return False

        try:
            async with self.database.lock:
                fields = ', '.join(f"{key} = ?" for key in kwargs.keys())
                values = list(kwargs.values()) + [user_id]

                query: str = await queries_line(48)
                query.replace('{fields}', ', '.join(fields))

                await self.database.conn.execute(query, values)
                await self.database.conn.commit()

            return True
        except aiosqlite.Error as error:
            await Logger.error(f"ID: {user_id} - SQL: {error}", False)
            return False