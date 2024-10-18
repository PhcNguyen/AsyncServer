# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.


from sources.handler.cmd import Cmd
from sources.model import types, utils
from sources.model.realtime import Realtime
from sources.manager.security import JwtManager, LoginAttempts



class CommandHandler:
    def __init__(self, sqlite: types.DatabaseManager):
        self.sqlite = sqlite
        self.login_attempts = LoginAttempts()

        # Ánh xạ các lệnh đến các phương thức xử lý tương ứng
        self.command_list = [
            (Cmd.LOGIN, self.handle_login),
            (Cmd.LOGOUT, self.handle_logout),
            (Cmd.REGISTER, self.handle_register),
            (Cmd.PLAYER_INFO, self.handle_player)
        ]

    async def handle_command(self, data):
        command = data.get("command")

        # Tìm hàm xử lý dựa trên lệnh trong danh sách
        for cmd, handler in self.command_list:
            if cmd == command:
                return await handler(data)

        return utils.Response.error(f"Lệnh không xác định: {command}")

    async def handle_login(self, data):
        some_threshold = 10  # Giới hạn thời gian tối thiểu giữa các lần đăng nhập

        email = data.get("email", "").lower()
        password = data.get("password", "")

        if not email or not password:
            return utils.Response.error("Thiếu email hoặc mật khẩu.")

        account_info = await self.sqlite.account.info(email)

        if account_info["last_login"]:
            time_last_login = Realtime.to_vietnam(account_info["last_login"])
            if Realtime.since(time_last_login) < some_threshold:
                return utils.Response.error("Đăng nhập quá nhanh. Vui lòng thử lại sau.")

        await self.sqlite.account.update_last_login(email)

        # Xác thực email và mật khẩu
        response = await self.sqlite.account.login(email, password)

        if response.get("status"):
            if account_info["is_online"]:
                return utils.Response.error("Tài khoản đang trực tuyến.")

            # Tạo token nếu đăng nhập thành công
            token = JwtManager.create_token(email)
            return utils.Response.success("Đăng nhập thành công.", token=token)
        else:
            return response  # Trả về thông báo lỗi từ response

    async def handle_logout(self, data):
        user_id = data.get("id", "")
        if user_id:
            await self.sqlite.account.logout(user_id)
            return utils.Response.success("Đăng xuất thành công.")

    async def handle_register(self, data: dict) -> dict:
        email = data.get("email", "")
        password = data.get("password", "")

        if not email or not password:
            return utils.Response.error("Cần có email và mật khẩu.")

        return await self.sqlite.account.register(email, password)

    async def handle_player(self, data: dict) -> dict:
        user_id = data.get("id")
        if user_id is None:
            return utils.Response.error("Thiếu ID người dùng.")

        try:
            user_id = int(user_id)  # Ép kiểu user_id thành int
        except ValueError:
            return utils.Response.error("ID người dùng không hợp lệ.")  # Xử lý lỗi nếu không thể ép kiểu

        player_info = await self.sqlite.player.get(user_id)
        return utils.Response.success("Thông tin người chơi đã được lấy.", player_info=player_info)