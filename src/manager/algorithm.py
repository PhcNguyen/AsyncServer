# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import os
import json
import typing

from src.security import rsa
from src.server.cmd import Cmd
from src.model.types import DBManager
from src.model.settings import AlgorithmSettings
from src.manager.utils import (
    isAnotherKeyServer,
    decrypted_data,
    encrypted_data
)


class AlgorithmHandler(AlgorithmSettings):
    def __init__(self, sql: DBManager) -> None:
        self.sqlite = sql

        self.public_key = None
        self.private_key = None

        self.message_callback = None

         # Khởi tạo cặp khóa RSA
        self._initialize_RsaKeys()
    
    def _initialize_RsaKeys(self):
        """Kiểm tra và tạo cặp khóa RSA nếu chưa tồn tại."""

        if not (os.path.exists(self.key_path["public"]) 
        and os.path.exists(self.key_path["private"])
        ):  
            """Tạo cặp khóa RSA mới và lưu vào file."""
            try:
                self._notify("Create a new RSA key pair and save it to a file.")
                self.public_key, self.private_key = rsa.newkeys(512)  # Tạo cặp khóa 512-bit

                with open(self.key_path["public"], "wb") as pub_file, \
                    open(self.key_path["private"], "wb") as priv_file:
                    pub_file.write(self.public_key.save_pkcs1())
                    priv_file.write(self.private_key.save_pkcs1())  

            except Exception as error:
                self._notify_error(f"Error creating a key: {error}")
        
        """Tải khóa RSA từ file."""
        try:
            self._notify("Download the RSA key from the file.")

            with open(self.key_path["public"], "rb") as pub_file, \
                 open(self.key_path["private"], "rb") as priv_file:
                self.public_key = rsa.PublicKey.load_pkcs1(pub_file.read())
                self.private_key = rsa.PrivateKey.load_pkcs1(priv_file.read())

        except Exception as error:
            self._notify_error(f"Error loading the lock: {error}")
    
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

    def handle_data(
        self, 
        client_address: tuple, 
        client_data: bytes
    ) -> bytes:
        """Xử lý dữ liệu từ client và trả về kết quả."""
        
        data = decrypted_data(
            client_data, 
            self.public_key, 
            self.private_key
        )

        if 'status' in data:
            return data

        # GET DATA 
        command  = data.get("command",   "Unknown")
        message  = data.get("message",   "Unknown")
        username = data.get("username", "Unknown")
        password = data.get("password", "Unknown")
        ip_address = data.get("ip_address", "Unknown")

        pub_key_client = data.get("pub_key_client", "Unknown")
        pub_key_server = data.get("pub_key_client", "Unknown")
        

        # Kiểm tra xem public_key_server đúng không
        if not isAnotherKeyServer(self.public_key, pub_key_server):
            result = {
                "status": True,
                "pub_key_server": self.public_key,
                "message": "This is your Public Key"
            }
            return json.dumps(result).encode("utf-8")
        

        """Xử lý các lệnh từ client."""

        if command == "Unknown":
            result = {
                "status": True,
                "pub_key_server": self.public_key,
                "message": "This is your Public Key"
            }
            return json.dumps(result).encode("utf-8")

        if command == Cmd.LOGIN:
            self.sqlite.login(username, password)
        
        elif command == Cmd.LOGOUT:
            # Logic cho LOGOUT có thể thêm vào sau này
            return "Logout not implemented"

        elif command == Cmd.REGISTER:
            self.sqlite.insert_account(username, password, ip_address)
        
        elif command == Cmd.CLIENT_INFO:
            self.sqlite.get_player_coin(username)