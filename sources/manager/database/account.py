
import bcrypt
import aiosqlite

from sources.model import types
from sources.model.logging import AsyncLogger
from sources.manager.database.utils import queries_line



class AccountManager:
    def __init__(self, db_manager: types.DatabaseManager):
        self.db_manager = db_manager

    async def insert_account(self, username: str, password: str) -> bool:
        """Register a new account in the account table."""
        async with self.db_manager.lock:
            try:
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                async with self.db_manager.conn:
                    if await self._account_exists(username):
                        await AsyncLogger.notify_error(f"Username '{username}' already exists.")
                        return False

                    await self.db_manager.conn.execute(await queries_line(7), (username, hashed_password))
                    await self.db_manager.conn.commit()
                await AsyncLogger.notify(f"Account '{username}' created successfully.")
                return True
            except aiosqlite.Error as error:
                await AsyncLogger.notify_error(f"Error creating account '{username}': {error}")
                return False

    async def _account_exists(self, username: str) -> bool:
        """Check if an account with the given username exists."""
        result = await self.db_manager.conn.execute(await queries_line(1), (username,))
        account_exists = await result.fetchone()
        return account_exists is not None