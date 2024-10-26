# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

from typing import Dict, Callable

from sources.utils import types
from sources.constants.cmd import Cmd, Codes
from sources.constants.result import ResultBuilder
from sources.handlers.client import PlayerCommands, AccountCommands



class CommandHandler:
    def __init__(self, database: types.SQLite | types.MySQL):
        self.database = database

        self.account = AccountCommands(database)
        self.player = PlayerCommands(database)

        # Liên kết mã lệnh số với các phương thức xử lý tương ứng
        self.command_list: Dict[int, Callable] = {
            Cmd.LOGIN: self.account.login,
            Cmd.LOGOUT: self.account.logout,
            Cmd.REGISTER: self.account.register,
            Cmd.PLAYER_INFO: self.player.player_info
        }

    async def process_command(self, data: dict):
        command_code = data.get("command")

        if not isinstance(command_code, int):
            return ResultBuilder.error(Codes.COMMAND_CODE_INVALID)

        handler = self.command_list.get(command_code)

        if callable(handler):
            return await handler(data)

        return ResultBuilder.error(Codes.ACCESS_DENIED)