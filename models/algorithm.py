
# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import time
import json
import base64
import hashlib



def generate_id(string: str) -> str:
    # Tạo chuỗi hash SHA-256 từ input string và timestamp
    hash_bytes = hashlib.sha256(f"{string}-{int(time.time() * 1000)}".encode()).digest()
    # Mã hóa hash thành chuỗi base64 và loại bỏ ký tự '='
    return base64.urlsafe_b64encode(hash_bytes).rstrip(b'=').decode()

