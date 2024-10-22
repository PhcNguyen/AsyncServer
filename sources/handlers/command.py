# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

from sources.utils import types
from sources.utils.cmd import Cmd
from sources.utils.response import ResponseBuilder
from sources.utils.realtime import TimeUtil
from sources.manager.security import JwtManager



class CommandHandler:
    def __init__(self, database: types.SQLite | types.MySQL):
        self.database = database

        # Mapping commands to corresponding handler methods
        self.command_list = {
            Cmd.LOGIN: self.handle_login,
            Cmd.LOGOUT: self.handle_logout,
            Cmd.REGISTER: self.handle_register,
            Cmd.PLAYER_INFO: self.handle_player
        }

    async def process_command(self, data: dict):
        command_name = data.get("command")
        command = None

        # Safely check if the command is valid
        try:
            command = Cmd[command_name]  # This allows accessing Cmd by name
        except KeyError:
            return ResponseBuilder.error(6001)

        handler = self.command_list.get(command)
        if handler:
            return await handler(data)

        return ResponseBuilder.error(6002)

    async def handle_login(self, data: dict):
        some_threshold = 20  # Minimum time threshold between logins

        email = data.get("email", "").lower()
        password = data.get("password", "")

        if not email or not password:
            return ResponseBuilder.error(6004)

        account_info = await self.database.account.info(email)

        if account_info["last_login"]:
            time_last_login = TimeUtil.to_vietnam(account_info["last_login"])
            if TimeUtil.since(time_last_login) < some_threshold:
                return ResponseBuilder.error(6005)

        await self.database.account.update_last_login(email)

        # Validate email and password
        response = await self.database.account.login(email, password)

        if response.get("status"):
            if account_info["active"]:
                return ResponseBuilder.error(6006)

            # Generate token if login is successful
            token = JwtManager.create_token(email)
            return ResponseBuilder.success(9001, token=token)
        else:
            return ResponseBuilder  # Return the error message from the ResponseBuilder

    async def handle_logout(self, data: dict):
        user_id = data.get("id")
        if user_id is None:
            return ResponseBuilder.error(6007)

        try:
            user_id = int(user_id)
        except ValueError:
            return ResponseBuilder.error(6007)

        await self.database.account.logout(user_id)
        return ResponseBuilder.success(9002)

    async def handle_register(self, data: dict):
        email = data.get("email", "")
        password = data.get("password", "")

        if not email or not password:
            return ResponseBuilder.error(6008)

        return await self.database.account.register(email, password)

    async def handle_player(self, data: dict):
        user_id = data.get("id")
        if user_id is None:
            return ResponseBuilder.error(6007)
        try:
            user_id = int(user_id)  # Cast user_id to int
        except ValueError:
            return ResponseBuilder.error(6007)

        info = await self.database.player.get(user_id)
        return ResponseBuilder.info(info=info)