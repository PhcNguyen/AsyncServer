# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

from datetime import datetime, timedelta
from sources.constants.result import ResultBuilder
from sources.manager.security import JwtManager
from sources.constants.textserver import Codes
from sources.handlers.utils import is_valid_user_id


class AccountCommands:
    def __init__(self, database):
        self.database = database

    async def login(self, data: dict) -> dict:
        email = data.get("email", "").lower()
        password = data.get("password", "")

        if not email or not password:
            return ResultBuilder.error(Codes.MISSING_CREDENTIALS)

        status, account_info = await self.database.account.info(email)

        if not account_info:
            return ResultBuilder.error(message="Tài khoản không tồn tại.")

        if account_info["last_login"]:
            last_login_time = account_info["last_login"]
            current_time = datetime.now()

            # Define the time limit for logins (e.g., 20 seconds)
            time_limit = timedelta(seconds=20)

            if current_time - last_login_time < time_limit:
                return ResultBuilder.error(Codes.LOGIN_TOO_FAST)

        await self.database.account.update_last_login(email)

        status, message = await self.database.account.login(email, password)

        if status:
            if not account_info["active"]:
                return ResultBuilder.error(Codes.ACCOUNT_ACTIVE)

            token = JwtManager.create_token(email)
            return ResultBuilder.success(Codes.LOGIN_SUCCESS, token=token)

        return ResultBuilder.error(message="Mật khẩu không đúng.")

    async def logout(self, data: dict) -> dict:
        user_id = data.get("id")
        if user_id is None or (user_id := is_valid_user_id(user_id)) is None:
            return ResultBuilder.error(Codes.USER_ID_INVALID)

        await self.database.account.logout(user_id)
        return ResultBuilder.success(Codes.LOGOUT_SUCCESS)

    async def register(self, data: dict) -> dict:
        email = data.get("email", "")
        password = data.get("password", "")

        if not email or not password:
            return ResultBuilder.error(Codes.MISSING_CREDENTIALS)

        status, message = await self.database.account.register(email, password)
        if status:
            return ResultBuilder.success(Codes.LOGIN_SUCCESS)

        # Return the error message from the registration process
        return ResultBuilder.error(message=message)
