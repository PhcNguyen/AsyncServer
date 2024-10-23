# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import bcrypt
import aiosqlite

from sources.utils import types
from sources.utils.response import ResponseBuilder
from sources.utils.sqlite import (
    queries_line,
    is_valid_email,
    is_valid_password
)



class AccountManager:
    def __init__(self, db: types.SQLite | types.MySQL):
        self.database = db

    async def _account_exists(self, email: str) -> bool:
        """Check if an account with the given email exists."""
        async with self.database.lock:
            result = await self.database.conn.execute(await queries_line(1), (email,))
            account_exists = await result.fetchone()
        return account_exists is not None

    async def info(self, email) -> dict:
        async with self.database.conn:  # Opening the connection
            result = await self.database.conn.execute(await queries_line(1), (email,))
            account = await result.fetchone()

            if account:
                account_info = {
                    "id": account[0],
                    "email": account[1],
                    "password": account[2],
                    "ban": account[3] == 1,
                    "role": account[4],
                    "active": account[5] == 1,
                    "last_login": account[6]
                }
                return account_info
        return {}

    async def register(self, email: str, password: str) -> dict:
        """Register a new account in the account table."""
        if not is_valid_email(email):
            return ResponseBuilder.error(message="Địa chỉ email không hợp lệ.")
        if not is_valid_password(password):
            return ResponseBuilder.error(message="Mật khẩu không đủ tiêu chuẩn.")

        async with self.database.lock:
            try:
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                async with self.database.conn:
                    if await self._account_exists(email):
                        return ResponseBuilder.error(message="Tài khoản đã tồn tại.")

                    await self.database.conn.execute(await queries_line(21), (email, hashed_password))
                    await self.database.conn.commit()
                return ResponseBuilder.success(message="Tạo tài khoản thành công.")
            except aiosqlite.Error as error:
                return ResponseBuilder.error(message="Lỗi khi tạo tài khoản.", error=error)

    async def login(self, email: str, password: str) -> dict:
        """Login with the given email and password."""
        async with self.database.lock:  # Ensure that locking is necessary
            try:
                account = await self.info(email)

                if not account:  # Check for an empty dict instead of None
                    return ResponseBuilder.error(message=f"Email '{email}' không tồn tại.")

                if account["ban"]:
                    return ResponseBuilder.error(message="Tài khoản đã bị khóa.")

                # Password check using bcrypt
                if bcrypt.checkpw(password.encode('utf-8'), account["password"]):
                    if account["active"]:
                        return ResponseBuilder.error(message="Người dùng đã đăng nhập từ trước.")

                    async with self.database.conn:
                        # Cập nhật trạng thái trực tuyến và đăng nhập
                        await self.database.conn.execute(await queries_line(42), (account["id"],))
                        await self.database.conn.commit()

                    account["message"] = "Người dùng đã đăng nhập thành công."
                    return account
                else:
                    return ResponseBuilder.error(message="Mật khẩu không đúng.")
            except aiosqlite.Error as error:
                return ResponseBuilder.error(message=f"Lỗi khi đăng nhập.", error=error)

    async def change_password(self, user_id: int, old_password: str, new_password: str) -> dict:
        """Change the user's password if the old password is correct."""

        # Validate the new password based on criteria
        if not is_valid_password(new_password):
            return ResponseBuilder.error(message="Mật khẩu mới không đủ tiêu chuẩn.")

        async with self.database.lock:
            try:
                # Retrieve the user's account information using the `info` function
                account = await self.info(user_id)

                if not account:  # If the account doesn't exist
                    return ResponseBuilder.error(message="Tài khoản không tồn tại.")

                stored_password = account["password"]  # Access the stored password from the info

                # Check if the provided old_password matches the stored hashed password
                if not bcrypt.checkpw(old_password.encode('utf-8'), stored_password):
                    return ResponseBuilder.error(message="Mật khẩu cũ không chính xác.")

                # Hash the new password
                hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

                # Update the password in the database
                async with self.database.conn:
                    await self.database.conn.execute(
                        await queries_line(41), (hashed_new_password, account["id"])
                    )
                    await self.database.conn.commit()  # Commit the changes

                return ResponseBuilder.success(message="Mật khẩu đã được thay đổi thành công.")

            except aiosqlite.Error as error:
                return ResponseBuilder.error(message=f"Lỗi khi thay đổi mật khẩu", error=error)

    async def lock(self, user_id: int) -> dict:
        async with self.database.lock:
            try:
                async with self.database.conn:
                    await self.database.conn.execute(await queries_line(44), (user_id,))
                    await self.database.conn.commit()

                    return ResponseBuilder.success(message="Tài khoản đã bị khóa thành công.")
            except Exception as error:
                return ResponseBuilder.error(message=f"Lỗi khi khóa tài khoản: {str(error)}")

    async def delete(self, user_id: int) -> dict:
        async with self.database.lock:
            try:
                async with self.database.conn:
                    await self.database.conn.execute(await queries_line(51), (user_id,))
                    await self.database.conn.commit()
                    return ResponseBuilder.success(message="Tài khoản đã được xóa thành công.")
            except Exception as error:
                return ResponseBuilder.error(message=f"Lỗi khi xóa tài khoản: {str(error)}")

    async def logout(self, user_id: int) -> dict:
        """Logout the user and update their status."""
        async with self.database.lock:
            try:
                async with self.database.conn:
                    await self.database.conn.execute(await queries_line(43), (user_id,))
                    await self.database.conn.commit()

                return ResponseBuilder.success(message="Người dùng đã đăng xuất thành công.")
            except Exception as error:
                return ResponseBuilder.error(message=f"Lỗi khi đăng xuất.", error=error)

    async def update_last_login(self, email = None, user_id: int = None) -> bool:
        if user_id is not None: data = user_id
        elif email is not None: data = email
        else: return False

        async with self.database.conn:
            await self.database.conn.execute(await queries_line(43), (data,))
            await self.database.conn.commit()
            return True