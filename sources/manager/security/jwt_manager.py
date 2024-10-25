# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import os
import jwt
import time
import secrets
import datetime
from sources.configs import file_paths
from sources.utils.realtime import TimeUtil



class JwtManager:
    SECRET_KEY = None

    @classmethod
    def _initialize_secret_key(cls):
        """Khởi tạo khóa bí mật từ tệp hoặc tạo mới nếu tệp không tồn tại hoặc khóa đã hết hạn."""
        filename = file_paths("secret.key")

        # Nếu tệp không tồn tại, tạo khóa mới
        if not os.path.exists(filename):
            cls.SECRET_KEY = secrets.token_hex(32)
            with open(filename, 'w') as file:
                file.write(cls.SECRET_KEY + '\n')  # Ghi khóa vào tệp
                file.write(f"{time.time()}\n")  # Ghi timestamp vào tệp
        else:
            with open(filename, 'r') as file:
                cls.SECRET_KEY = file.readline().strip()  # Đọc khóa
                created_time = float(file.readline().strip())  # Đọc timestamp

            # Kiểm tra xem khóa đã quá hạn chưa (1 tháng = 30 ngày)
            if time.time() - created_time > (30 * 24 * 60 * 60):  # 30 ngày
                cls.SECRET_KEY = secrets.token_hex(32)
                with open(filename, 'w') as file:
                    file.write(cls.SECRET_KEY + '\n')  # Cập nhật khóa mới
                    file.write(f"{time.time()}\n")  # Cập nhật timestamp mới

    @classmethod
    def initialize(cls):
        """Khởi động lớp JwtManager, đảm bảo khóa bí mật tồn tại."""
        cls._initialize_secret_key()

    @staticmethod
    def create_token(email: str) -> str:
        """Tạo token JWT với email và thời gian hết hạn."""
        payload = {
            "email": email,
            "exp": TimeUtil.now_vietnam() + datetime.timedelta(hours=2)  # Token hết hạn sau 2 giờ
        }
        return jwt.encode(payload, JwtManager.SECRET_KEY, algorithm="HS256")

    @staticmethod
    def verify_token(token: str) -> dict:
        """Xác minh tính hợp lệ của token và trả về payload nếu hợp lệ."""
        try:
            payload = jwt.decode(token, JwtManager.SECRET_KEY, algorithms=["HS256"])
            return payload  # Trả về payload nếu token hợp lệ

        except jwt.ExpiredSignatureError:
            raise Exception("Token has expired")

        except jwt.InvalidTokenError:
            raise Exception("Invalid token")

        except Exception as e:
            raise Exception(f"Token verification error: {str(e)}")

    @staticmethod
    def decode_token(token: str) -> str:
        """Giải mã token JWT và trả về email."""
        try:
            payload = jwt.decode(token, JwtManager.SECRET_KEY, algorithms=["HS256"])
            return payload["email"]
        except jwt.ExpiredSignatureError:
            raise Exception("Token has expired")

        except jwt.InvalidTokenError:
            raise Exception("Invalid token")

        except Exception as e:
            raise Exception(f"Token decoding error: {str(e)}")


# Khởi động JwtManager
JwtManager.initialize()