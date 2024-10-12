
# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import time
import json
import base64
import hashlib



class Algorithm:
    def __init__(self, sql) -> None:
        self.sql = sql

    @staticmethod
    def generate_id(string: str) -> str:
        # Tạo chuỗi hash SHA-256 từ input string và timestamp
        hash_bytes = hashlib.sha256(f"{string}-{int(time.time() * 1000)}".encode()).digest()
        # Mã hóa hash thành chuỗi base64 và loại bỏ ký tự '='
        return base64.urlsafe_b64encode(hash_bytes).rstrip(b'=').decode()


    def handle_data(self, client_address: tuple, data: dict) -> bytes:
        """Xử lý dữ liệu từ client và trả về kết quả."""
        # Nếu data là bytes, giải mã và chuyển sang JSON
        if isinstance(data, bytes):
            try:
                data = data.decode('utf-8')
                data = json.loads(data)
            except (UnicodeDecodeError, json.JSONDecodeError) as e:
                return f"Error decoding data: {e}".encode()

        # Kiểm tra định dạng data có đúng là dict không
        if not isinstance(data, dict):
            return "Invalid data format".encode()
        
        return data