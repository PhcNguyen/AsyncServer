import bcrypt
import aiosqlite
from sources.utils import types
from sources.utils.sql import (
    queries_line,
    is_valid_email,
    is_valid_password
)


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

    async def info(self, data: str | int = None) -> (bool, dict | str):
        """Retrieve account information based on email or user ID."""
        if data is None:
            return False, "No data provided."

        queries = await queries_line(1) if data.isdigit() else await queries_line(7)
        data = int(data) if isinstance(data, str) and data.isdigit() else data

        result = await self._execute(queries, (data,))
        account = await result.fetchone()

        if account:
            return True, {
                "id": account[0],
                "email": account[1],
                "password": account[2],
                "ban": account[3] == 1,
                "role": account[4],
                "active": account[5] == 1,
                "last_login": account[6]
            }
        else:
            return False, "Account not found."

    async def register(self, email: str, password: str) -> (bool, str):
        """Register a new account."""
        if not is_valid_email(email):
            return False, "Địa chỉ email không hợp lệ."
        if not is_valid_password(password):
            return False, "Mật khẩu không đủ tiêu chuẩn."

        try:
            if await self._account_exists(email):
                return False, "Tài khoản đã tồn tại."

            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            await self._execute(await queries_line(21), (email, hashed_password))
            await self._commit()
            return True, "Tạo tài khoản thành công."

        except aiosqlite.Error as error:
            return False, f"Lỗi khi tạo tài khoản: {error}"

    async def login(self, email: str, password: str) -> (bool, str):
        """Login with the given email and password."""
        try:
            success, account = await self.info(email)
            if not success:
                return False, account  # Return the error message

            if account["ban"]:
                return False, "Tài khoản đã bị khóa."

            if bcrypt.checkpw(password.encode('utf-8'), account["password"]):
                if not account["active"]:
                    return False, "Tài khoản chưa được kích hoạt."

                # Update last login time
                await self.update_last_login(email=email)

                return True, "Người dùng đã đăng nhập thành công."

            return False, "Mật khẩu không đúng."

        except aiosqlite.Error as error:
            return False, f"Lỗi khi đăng nhập: {error}"

    async def change_password(self, user_id: int, old_password: str, new_password: str) -> (bool, str):
        """Change the user's password if the old password is correct."""
        if not is_valid_password(new_password):
            return False, "Mật khẩu mới không đủ tiêu chuẩn."

        success, account = await self.info(user_id)
        if not success:
            return False, account  # Return the error message

        if not bcrypt.checkpw(old_password.encode('utf-8'), account["password"]):
            return False, "Mật khẩu cũ không chính xác."

        hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        await self._execute(await queries_line(41), (hashed_new_password, account["id"]))
        await self._commit()

        return True, "Mật khẩu đã được thay đổi thành công."

    async def lock(self, user_id: int) -> (bool, str):
        """Lock the user account."""
        await self._execute(await queries_line(44), (user_id,))
        await self._commit()

        return True, "Tài khoản đã bị khóa thành công."

    async def delete(self, user_id: int) -> (bool, str):
        """Delete the user account."""
        await self._execute(await queries_line(51), (user_id,))
        await self._commit()

        return True, "Tài khoản đã được xóa thành công."

    async def logout(self, user_id: int) -> (bool, str):
        """Logout the user and update their status."""
        await self._execute(await queries_line(43), (user_id,))
        await self._commit()

        return True, "Người dùng đã đăng xuất thành công."

    async def update_last_login(self, email=None, user_id: int = None) -> (bool, str):
        """Update the last login timestamp."""
        if user_id is not None:
            await self._execute(await queries_line(43), (user_id,))
        elif email is not None:
            await self._execute(await queries_line(43), (email,))
        else:
            return False, "Không có thông tin để cập nhật."

        await self._commit()
        return True, "Thời gian đăng nhập đã được cập nhật."