# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import bcrypt
import aiosqlite

from sources.model import types, utils
from sources.manager.sqlite.utils import (
    queries_line,
    is_valid_email,
    is_valid_password
)



class AccountManager:
    def __init__(self, db_manager: types.DatabaseManager):
        self.db_manager = db_manager

    async def _account_exists(self, email: str) -> bool:
        """Check if an account with the given email exists."""
        async with self.db_manager.lock:
            result = await self.db_manager.conn.execute(await queries_line(1), (email,))
            account_exists = await result.fetchone()
        return account_exists is not None

    async def register(self, email: str, password: str) -> dict:
        """Register a new account in the account table."""
        if not is_valid_email(email):
            return utils.Response.error("Địa chỉ email không hợp lệ.")
        if not is_valid_password(password):
            return utils.Response.error("Mật khẩu không đủ tiêu chuẩn.")

        async with self.db_manager.lock:
            try:
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                async with self.db_manager.conn:
                    if await self._account_exists(email):
                        return utils.Response.error("Tài khoản đã tồn tại.")

                    await self.db_manager.conn.execute(await queries_line(21), (email, hashed_password))
                    await self.db_manager.conn.commit()
                return utils.Response.success("Tạo tài khoản thành công.")
            except aiosqlite.Error:
                return utils.Response.error("Lỗi khi tạo tài khoản.")

    async def login(self, email: str, password: str) -> dict:
        """Login with the given email and password."""
        async with self.db_manager.lock:
            try:
                async with self.db_manager.conn:
                    result = await self.db_manager.conn.execute(await queries_line(1), (email,))
                    account = await result.fetchone()

                if account is None:
                    return utils.Response.error(f"Email '{email}' không tồn tại.")

                user_id = account[0]
                stored_password = account[1]
                is_lock = account[2] == 1
                role = account[3]
                is_online = account[4] == 1
                is_login = account[5] == 1

                if is_lock:
                    return utils.Response.error("Tài khoản đã bị khóa.")

                if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                    if is_login or is_online:
                        return utils.Response.error("Người dùng đã đăng nhập từ trước.")

                    async with self.db_manager.conn:
                        # Cập nhật trạng thái trực tuyến và đăng nhập
                        await self.db_manager.conn.execute(await queries_line(42), (user_id,))
                        await self.db_manager.conn.commit()

                    return utils.Response.success("Người dùng đã đăng nhập thành công.", id=user_id, role=role)
                else:
                    return utils.Response.error("Mật khẩu không đúng.")
            except aiosqlite.Error as error:
                return utils.Response.error(f"Lỗi khi đăng nhập cho '{email}': {error}")

    async def info(self, email):
        async with self.db_manager.conn:
            result = await self.db_manager.conn.execute(await queries_line(1), (email,))
            account = await result.fetchone()

        account_info = {
            "user_id": account[0],
            "stored_password": account[1],
            "is_lock": account[2] == 1,
            "role": account[3],
            "is_online": account[4] == 1,
            "is_login": account[5] == 1,
            "last_login": account[6],
            "create_time": account[7],
            "updated_last": account[8]
        }

        return account_info

    async def change_password(self, user_id: int, old_password: str, new_password: str) -> dict:
        """Change the user's password if the old password is correct."""
        if not is_valid_password(new_password):
            return utils.Response.error("Mật khẩu mới không đủ tiêu chuẩn.")

        async with self.db_manager.lock:
            try:
                async with self.db_manager.conn:
                    result = await self.db_manager.conn.execute(await queries_line(1), (user_id,))
                    account = await result.fetchone()

                    if account is None:
                        return utils.Response.error("Tài khoản không tồn tại.")

                    stored_password = account[1]

                    if not bcrypt.checkpw(old_password.encode('utf-8'), stored_password):
                        return utils.Response.error("Mật khẩu cũ không chính xác.")

                    hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

                    await self.db_manager.conn.execute(
                        await queries_line(41), (hashed_new_password, user_id)
                    )
                    await self.db_manager.conn.commit()

                    return utils.Response.success("Mật khẩu đã được thay đổi thành công.")
            except aiosqlite.Error as error:
                return utils.Response.error(f"Lỗi khi thay đổi mật khẩu: {error}")

    async def lock(self, user_id: int) -> dict:
        async with self.db_manager.lock:
            try:
                async with self.db_manager.conn:
                    await self.db_manager.conn.execute(await queries_line(44), (user_id,))
                    await self.db_manager.conn.commit()

                    return utils.Response.success("Tài khoản đã bị khóa thành công.")
            except Exception as error:
                return utils.Response.error(f"Lỗi khi khóa tài khoản: {str(error)}")

    async def delete(self, user_id: int) -> dict:
        async with self.db_manager.lock:
            try:
                async with self.db_manager.conn:
                    await self.db_manager.conn.execute(await queries_line(51), (user_id,))
                    await self.db_manager.conn.commit()
                    return utils.Response.success("Tài khoản đã được xóa thành công.")
            except Exception as error:
                return utils.Response.error(f"Lỗi khi xóa tài khoản: {str(error)}")

    async def logout(self, user_id: int) -> dict:
        """Logout the user and update their status."""
        async with self.db_manager.lock:
            try:
                async with self.db_manager.conn:
                    await self.db_manager.conn.execute(await queries_line(43), (user_id,))
                    await self.db_manager.conn.commit()

                return utils.Response.success("Người dùng đã đăng xuất thành công.")
            except Exception as error:
                return utils.Response.error(f"Lỗi khi đăng xuất: {str(error)}")

    async def update_last_login(self, email):
        async with self.db_manager.conn:
            await self.db_manager.conn.execute(await queries_line(43), (email,))