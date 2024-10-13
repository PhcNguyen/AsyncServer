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

def isAnotherKeyServer(
    pubic_key: rsa.PublicKey,
    pub_key_server: rsa.PublicKey
) -> bool:
    '''
    pubic_key: Keys saved on the server

    pub_key_server: Server key sends to the user
    '''
    return pub_key_server == pubic_key


def decrypted_data(
    client_data: bytes,
    public_key: rsa.PublicKey, 
    private_key: rsa.PrivateKey
) -> typing.Dict:
    """Giải mã dữ liệu."""
    try:
        decrypted_data = rsa.decrypt(client_data, private_key)
        data = decrypted_data.decode("utf-8")
        data = json.loads(data)
        # Kiểm tra định dạng data có đúng là dict không
        if not isinstance(data, dict):
            return {
                "status": False,
                "pub_key_server": public_key,
                "message": "Invalid data format"
            }
    except (rsa.DecryptionError, UnicodeDecodeError, json.JSONDecodeError) as e:
        return {
            "status": False,
            "pub_key_server": public_key,
            "message": str(e)
        }
    
    return data


def encrypted_data(
    
) -> bytes: pass