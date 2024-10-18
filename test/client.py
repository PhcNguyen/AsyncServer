# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

class Client:
    def __init__(self):
        self.token = None

    async def login(self, username, password):
        # Sau khi đăng nhập thành công, lưu token
        response = await self.send_login_data(username, password)
        if response.get("status"):
            self.token = response.get("token")

    async def send_request(self, data):
        if not self.token:
            raise Exception("You must login first")
        data["token"] = self.token
        await self.send_data(data)

    async def send_login_data(self, username, password) -> dict: ...
    async def send_data(self, data) -> dict: ...