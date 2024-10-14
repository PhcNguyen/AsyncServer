# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import typing

from sources.application.cmd import Cmd
from sources.model.types import DBManager
from sources.model.security.cipher import Cipher
from sources.application.configs import Configs



class AlgorithmProcessing(Configs.DirPath):
    def __init__(self, sql: DBManager) -> None:
        self.sqlite = sql

        self.cipher = None
        self.public_key = None
        self.private_key = None

        self.message_callback = None

        self._load_keys()
    
    def _load_keys(self):
        self.cipher = Cipher(self.key_path)
        self.public_key = self.cipher.public_key
        self.private_key = self.cipher.private_key
    
    def _notify(self, message):
        """Notification method."""
        if self.message_callback:
            self.message_callback(f"Error: {message}")
    
    def _notify_error(self, message):
        """Error notification method."""
        if self.message_callback:
            self.message_callback(f"Error: {message}")
    
    def set_message_callback(
        self, callback: 
        typing.Callable[[str], None]
    ):  self.message_callback = callback

    async def close(self):
        await self.sqlite.close()

    async def handle_data(
        self, 
        client_address: tuple, 
        client_data: bytes
    ) -> bytes:
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
            self.sqlite.login(username, password)
        
        elif command == Cmd.LOGOUT:
            # Logic cho LOGOUT có thể thêm vào sau này
            return "Logout not implemented"

        elif command == Cmd.REGISTER:
            self.sqlite.insert_account(username, password, ip_address)
        
        elif command == Cmd.CLIENT_INFO:
            self.sqlite.get_player_coin(username)