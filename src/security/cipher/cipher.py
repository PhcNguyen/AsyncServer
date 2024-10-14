# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import os
import json
import typing

from src.security import rsa


class Cipher:
    def __init__(
        self, key_path: str
    ) -> None:
        """Khởi tạo với khóa riêng của máy và khóa công khai của đối phương."""
        self.key_path = key_path
        self.private_key = None
        self.public_key = None

        self._initialize_RsaKeys()
    
    def _initialize_RsaKeys(self):
        """Kiểm tra và tạo cặp khóa RSA nếu chưa tồn tại."""
        if not (os.path.exists(self.key_path["public"]) 
                and os.path.exists(self.key_path["private"])):
            """Tạo cặp khóa RSA mới và lưu vào file."""
            self.public_key, self.private_key = rsa.newkeys(512)  # Tạo cặp khóa 512-bit

            with open(self.key_path["public"], "wb") as pub_file, \
                open(self.key_path["private"], "wb") as priv_file:
                pub_file.write(self.public_key.save_pkcs1())
                priv_file.write(self.private_key.save_pkcs1())  

        """Tải khóa RSA từ file."""
        with open(self.key_path["public"], "rb") as pub_file:
            pub_key_data = pub_file.read()  # Read public key data first
            self.public_key = rsa.PublicKey.load_pkcs1(pub_key_data)

        with open(self.key_path["private"], "rb") as priv_file:
            priv_key_data = priv_file.read()  # Read private key data
            self.private_key = rsa.PrivateKey.load_pkcs1(priv_key_data)

    def encrypt(
        self, 
        data: typing.Dict
    ) -> typing.Optional[bytes]:
        """Mã hóa dữ liệu bằng khóa công khai."""
        try:
            # Mã hóa dữ liệu sử dụng khóa công khai của đối phương
            encrypted_message = rsa.encrypt(
                json.dumps(data).encode("utf-8"), 
                self.public_key
            )
            return encrypted_message
        except Exception:
            return None

    def decrypt(
        self, 
        encrypted_data: bytes
    ) -> typing.Optional[typing.Dict]:
        """Giải mã dữ liệu bằng khóa riêng."""
        try:
            decrypted_message = rsa.decrypt(encrypted_data, self.private_key)
            decrypted_text = decrypted_message.decode("utf-8")

            return json.loads(decrypted_text)
        except (rsa.DecryptionError, UnicodeDecodeError, json.JSONDecodeError):
            return None