# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import os
import jwt
import time
import secrets
import datetime
from sources.configs import file_paths



def secret_key_file():
    filename = file_paths("secret.key")

    # Kiểm tra xem file có tồn tại không
    if not os.path.exists(filename):
        secret_key = secrets.token_hex(32)
        with open(filename, 'w') as file:
            file.write(secret_key)
            file.write(f"\n{time.time()}")  # Ghi timestamp vào file
    else:
        # Đọc khóa từ file
        with open(filename, 'r') as file:
            secret_key = file.readline().strip()
            created_time = float(file.readline().strip())  # Đọc timestamp

        # Kiểm tra xem khóa đã quá hạn chưa (1 tháng = 30 ngày)
        if time.time() - created_time > (30 * 24 * 60 * 60):  # 30 ngày
            secret_key = secrets.token_hex(32)
            with open(filename, 'w') as file:
                file.write(secret_key)
                file.write(f"\n{time.time()}")  # Cập nhật timestamp mới

    return secret_key



class JwtManager:
    SECRET_KEY = secret_key_file()

    @staticmethod
    def create_token(username):
        payload = {
            "username": username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)  # Token hết hạn sau 2 giờ
        }
        return jwt.encode(payload, JwtManager.SECRET_KEY, algorithm="HS256")

    @staticmethod
    def decode_token(token):
        try:
            payload = jwt.decode(token, JwtManager.SECRET_KEY, algorithms=["HS256"])
            return payload["username"]
        except jwt.ExpiredSignatureError:
            raise Exception("Token has expired")
        except jwt.InvalidTokenError:
            raise Exception("Invalid token")