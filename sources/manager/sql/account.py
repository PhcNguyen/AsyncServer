# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import bcrypt
import aiosqlite
from sources.utils import types
from sources.utils.sql import (
    queries_line,
    is_valid_email,
    is_valid_password
)
from sources.utils.result import ResultBuilder



class SQLAccount:
    def __init__(self, db: types.SQLite | types.MySQL):
        self.database = db

    async def _execute(self, query: str, params: tuple = ()) -> aiosqlite.Cursor:
        """Helper function to execute a query."""
        async with self.database.lock:
            async with self.database.conn.execute(query, params) as cursor:
                return cursor

    async def _commit(self):
        """Helper function to commit the transaction."""
        async with self.database.lock:
            await self.database.conn.commit()

    async def _account_exists(self, email: str) -> bool:
        """Check if an account with the given email exists."""
        result = await self._execute(await queries_line(1), (email,))
        return await result.fetchone() is not None

    async def info(self, data: str | int = None) -> dict:
        """Retrieve account information based on email or user ID."""
        if data is None:
            return {}  # Early return if no data is provided

        queries = await queries_line(1) if data.isdigit() else await queries_line(7)
        result = await self._execute(queries, (data,))
        account = await result.fetchone()

        # Return account information if found, else return an empty dictionary
        return {
            "id": account[0],
            "email": account[1],
            "password": account[2],
            "ban": account[3] == 1,
            "role": account[4],
            "active": account[5] == 1,
            "last_login": account[6]
        } if account else {}

    async def register(self, email: str, password: str) -> dict:
        """Register a new account."""
        if not is_valid_email(email):
            return ResultBuilder.error(message="Địa chỉ email không hợp lệ.")
        if not is_valid_password(password):
            return ResultBuilder.error(message="Mật khẩu không đủ tiêu chuẩn.")

        try:
            if await self._account_exists(email):
                return ResultBuilder.error(message="Tài khoản đã tồn tại.")

            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            await self._execute(await queries_line(21), (email, hashed_password))
            await self._commit()
            return ResultBuilder.success(message="Tạo tài khoản thành công.")
        except aiosqlite.Error as error:
            return ResultBuilder.error(message="Lỗi khi tạo tài khoản.", error=str(error))

    async def login(self, email: str, password: str) -> dict:
        """Login with the given email and password."""
        try:
            account = await self.info(email)
            if not account:
                return ResultBuilder.error(message=f"Email '{email}' không tồn tại.")
            if account["ban"]:
                return ResultBuilder.error(message="Tài khoản đã bị khóa.")

            if bcrypt.checkpw(password.encode('utf-8'), account["password"]):
                if account["active"]:
                    return ResultBuilder.error(message="Người dùng đã đăng nhập từ trước.")

                await self._execute(await queries_line(42), (account["id"],))
                await self._commit()
                return {**account, "message": "Người dùng đã đăng nhập thành công."}
            return ResultBuilder.error(message="Mật khẩu không đúng.")
        except aiosqlite.Error as error:
            return ResultBuilder.error(message="Lỗi khi đăng nhập.", error=str(error))

    async def change_password(self, user_id: int, old_password: str, new_password: str) -> dict:
        """Change the user's password if the old password is correct."""
        if not is_valid_password(new_password):
            return ResultBuilder.error(message="Mật khẩu mới không đủ tiêu chuẩn.")

        account = await self.info(user_id)
        if not account:
            return ResultBuilder.error(message="Tài khoản không tồn tại.")

        if not bcrypt.checkpw(old_password.encode('utf-8'), account["password"]):
            return ResultBuilder.error(message="Mật khẩu cũ không chính xác.")

        hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        await self._execute(await queries_line(41), (hashed_new_password, account["id"]))
        await self._commit()
        return ResultBuilder.success(message="Mật khẩu đã được thay đổi thành công.")

    async def lock(self, user_id: int) -> dict:
        """Lock the user account."""
        await self._execute(await queries_line(44), (user_id,))
        await self._commit()
        return ResultBuilder.success(message="Tài khoản đã bị khóa thành công.")

    async def delete(self, user_id: int) -> dict:
        """Delete the user account."""
        await self._execute(await queries_line(51), (user_id,))
        await self._commit()
        return ResultBuilder.success(message="Tài khoản đã được xóa thành công.")

    async def logout(self, user_id: int) -> dict:
        """Logout the user and update their status."""
        await self._execute(await queries_line(43), (user_id,))
        await self._commit()
        return ResultBuilder.success(message="Người dùng đã đăng xuất thành công.")

    async def update_last_login(self, email=None, user_id: int = None) -> bool:
        """Update the last login timestamp."""
        if user_id is not None:
            await self._execute(await queries_line(43), (user_id,))
        elif email is not None:
            await self._execute(await queries_line(43), (email,))
        else:
            return False
        await self._commit()
        return True