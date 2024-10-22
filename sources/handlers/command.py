# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

from sources.utils import types
from sources.utils.cmd import Cmd
from sources.utils.system import Response
from sources.utils.realtime import TimeUtil
from sources.manager.security import JwtManager



class CommandHandler:
    def __init__(self, sql: types.SQLite | types.MySQL):
        self.sqlite = sql

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
            return Response.error(f"Unknown command: {command_name}")

        handler = self.command_list.get(command)
        if handler:
            return await handler(data)

        return Response.error(f"Handler not found for command: {command}")

    async def handle_login(self, data: dict):
        some_threshold = 20  # Minimum time threshold between logins

        email = data.get("email", "").lower()
        password = data.get("password", "")

        if not email or not password:
            return Response.error("Thiếu email hoặc mật khẩu.")

        account_info = await self.sqlite.account.info(email)

        if account_info["last_login"]:
            time_last_login = TimeUtil.to_vietnam(account_info["last_login"])
            if TimeUtil.since(time_last_login) < some_threshold:
                return Response.error("Bạn đã đăng nhập tài khoản quá nhanh. Vui lòng thử lại sau ít phút.")

        await self.sqlite.account.update_last_login(email)

        # Validate email and password
        response = await self.sqlite.account.login(email, password)

        if response.get("status"):
            if account_info["active"]:
                return Response.error("Tài khoản đang trực tuyến.")

            # Generate token if login is successful
            token = JwtManager.create_token(email)
            return Response.success("Đăng nhập thành công.", token=token)
        else:
            return response  # Return the error message from the response

    async def handle_logout(self, data: dict):
        user_id = data.get("id")
        if user_id is None:
            return Response.error("Thiếu ID người dùng.")

        try:
            user_id = int(user_id)
        except ValueError:
            return Response.error("ID người dùng không hợp lệ.")

        await self.sqlite.account.logout(user_id)
        return Response.success("Đăng xuất thành công.")

    async def handle_register(self, data: dict):
        email = data.get("email", "")
        password = data.get("password", "")

        if not email or not password:
            return Response.error("Cần có email và mật khẩu.")

        return await self.sqlite.account.register(email, password)

    async def handle_player(self, data: dict):
        user_id = data.get("id")
        if user_id is None:
            return Response.error("Thiếu ID người dùng.")

        try:
            user_id = int(user_id)  # Cast user_id to int
        except ValueError:
            return Response.error("ID người dùng không hợp lệ.")

        player_info = await self.sqlite.player.get(user_id)
        return Response.success("Thông tin người chơi đã được lấy.", player_info=player_info)
