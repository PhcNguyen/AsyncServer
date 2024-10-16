# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import typing

from sources.model import types
from sources.application.cmd import Cmd
from sources.model.security.cipher import Cipher
from sources.application.configs import Configs
from sources.model.logging.serverlogger import AsyncLogger


class AlgorithmProcessing:
    def __init__(self, sql: types.DatabaseManager) -> None:
        self.sqlite = sql

        self.cipher = None
        self.public_key = None
        self.private_key = None

        self._load_keys()
    
    def _load_keys(self):
        self.cipher = Cipher(
            Configs.FILE_PATHS["public_key.pem"],
            Configs.FILE_PATHS["private_key.pem"]
        )
        self.public_key = self.cipher.public_key
        self.private_key = self.cipher.private_key

    async def close(self):
        await self.sqlite.close()

    async def handle_data(
        self, 
        client_address: typing.Tuple[str, int],
        client_data: dict | bytes
    ) -> dict[str, str | bool | typing.Any] | str:
        """Xử lý dữ liệu từ client và trả về kết quả."""
        
        data = self.cipher.decrypt(client_data)

        if data is None:
            return {
                "status": False,
                "message": "Decryption failed: No data returned.",
                "key_server": self.public_key
            }

        # GET DATA 
        command  = data.get("command",  "")
        username = data.get("username", "")
        password = data.get("password", "")
        ip_address = data.get("ip_address", "")

        key_client = data.get("key_client", "")
        key_server = data.get("key_server", "")

        """Xử lý các lệnh từ client."""

        if command == Cmd.LOGIN:
            await self.sqlite.login(username, password)
        
        elif command == Cmd.LOGOUT:
            # Logic cho LOGOUT có thể thêm vào sau này
            return "Logout not implemented"

        elif command == Cmd.REGISTER:
            await self.sqlite.insert_account(username, password, ip_address)
        
        elif command == Cmd.PLAYER_INFO:
            await self.sqlite.get_player_coin(username)