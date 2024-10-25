# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

from sources.utils.result import ResultBuilder
from sources.manager.security import JwtManager
from sources.handlers.const import Codes
from sources.handlers.utils import is_valid_user_id



class AccountCommands:
    def __init__(self, database):
        self.database = database

    async def login(self, data: dict):
        email = data.get("email", "").lower()
        password = data.get("password", "")

        if not email or not password:
            return ResultBuilder.error(Codes.MISSING_CREDENTIALS)

        account_info = await self.database.account.info(email)

        if account_info["last_login"]:
            # Implement your last login logic
            pass

        await self.database.account.update_last_login(email)

        response = await self.database.account.login(email, password)

        if response.get("status"):
            if not account_info["active"]:
                return ResultBuilder.error(Codes.ACCOUNT_ACTIVE)

            token = JwtManager.create_token(email)
            return ResultBuilder.success(Codes.LOGIN_SUCCESS, token=token)

        return ResultBuilder.error(Codes.MISSING_CREDENTIALS)

    async def logout(self, data: dict):
        user_id = data.get("id")
        if user_id is None or (user_id := is_valid_user_id(user_id)) is None:
            return ResultBuilder.error(Codes.USER_ID_INVALID)

        await self.database.account.logout(user_id)
        return ResultBuilder.success(Codes.LOGOUT_SUCCESS)

    async def register(self, data: dict):
        email = data.get("email", "")
        password = data.get("password", "")

        if not email or not password:
            return ResultBuilder.error(Codes.MISSING_CREDENTIALS)

        return await self.database.account.register(email, password)