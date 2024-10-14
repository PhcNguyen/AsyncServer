# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import json
import time
import base64
import typing
import hashlib

from src.security import rsa



def generate_id(string: str) -> str:
    """Tạo chuỗi hash SHA-256 từ input string và timestamp."""
    hash_bytes = hashlib.sha256(f"{string}-{int(time.time() * 1000)}".encode()).digest()
    # Mã hóa hash thành chuỗi base64 và loại bỏ ký tự "="
    return base64.urlsafe_b64encode(hash_bytes).rstrip(b"=").decode()


def checkForDuplicateKeys(
    pubic_key: rsa.PublicKey,
    key_server: rsa.PublicKey
) -> bool:
    '''
    pubic_key: Keys saved on the server

    pub_key_server: Server key sends to the user
    '''
    return key_server == pubic_key

def checkUserKey(
    key_client: rsa.PublicKey
) -> bool:
    return key_client != ""