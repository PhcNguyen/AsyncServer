# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

from sources.utils.result import ResultBuilder
from sources.manager.security import JwtManager
from sources.handlers.const import Codes
from sources.handlers.utils import is_valid_user_id



class PlayerCommands:
    def __init__(self, database):
        self.database = database

    async def player_info(self, data: dict):
        token = data.get("token")
        if not token:
            return ResultBuilder.error(Codes.TOKEN_REQUIRED)

        try:
            JwtManager.verify_token(token)
        except Exception as error:
            return ResultBuilder.error(Codes.TOKEN_INVALID, error=error)

        user_id = data.get("id")
        if user_id is None or (user_id := is_valid_user_id(user_id)) is None:
            return ResultBuilder.error(Codes.USER_ID_INVALID)

        info = await self.database.player.get(user_id)
        if info is None:
            return ResultBuilder.error(Codes.PLAYER_INFO_NOT_FOUND)

        return ResultBuilder.info(info=info)