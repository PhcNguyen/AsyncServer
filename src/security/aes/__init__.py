
# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified TUDL License.

import base64

from lib.Crypto.Cipher import AES
from lib.Crypto.Protocol.KDF import PBKDF2
from lib.Crypto.Util.Padding import pad, unpad
from lib.Crypto.Random import get_random_bytes



def generate_key(password: str, salt: bytes, iterations: int = 100000) -> bytes:
    """
    Generate a key from the given password and salt using PBKDF2.
    
    :param password: The password to derive the key from.
    :param salt: A random salt to make the key generation more secure.
    :param iterations: The number of iterations for the key derivation function.
    :return: Derived key.
    """
    return PBKDF2(password, salt, dkLen=32, count=iterations)


def encrypt(data: str, password: str) -> dict:
    """
    Encrypt the given data using AES encryption.
    
    :param data: The plaintext data to encrypt.
    :param password: The password to derive the encryption key.
    :return: A dictionary containing the salt, nonce, and ciphertext.
    """
    salt = get_random_bytes(16)  # Generate a random salt
    key = generate_key(password, salt)  # Generate key from password and salt
    
    cipher = AES.new(key, AES.MODE_GCM)  # Create AES cipher in GCM mode
    ciphertext, tag = cipher.encrypt_and_digest(pad(data.encode(), AES.block_size))
    
    # Return the salt, nonce, and ciphertext encoded in base64 for easier storage/transmission
    return {
        'salt': base64.b64encode(salt).decode('utf-8'),
        'nonce': base64.b64encode(cipher.nonce).decode('utf-8'),
        'ciphertext': base64.b64encode(ciphertext).decode('utf-8'),
        'tag': base64.b64encode(tag).decode('utf-8')
    }


def decrypt(encrypted_data: dict, password: str) -> str:
    """
    Decrypt the given encrypted data using AES encryption.
    
    :param encrypted_data: A dictionary containing the salt, nonce, ciphertext, and tag.
    :param password: The password to derive the decryption key.
    :return: The decrypted plaintext data.
    """
    salt = base64.b64decode(encrypted_data['salt'])
    nonce = base64.b64decode(encrypted_data['nonce'])
    ciphertext = base64.b64decode(encrypted_data['ciphertext'])
    tag = base64.b64decode(encrypted_data['tag'])
    
    key = generate_key(password, salt)  # Generate key from password and salt
    
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)  # Create AES cipher in GCM mode
    plaintext = unpad(cipher.decrypt_and_verify(ciphertext, tag), AES.block_size)
    
    return plaintext.decode('utf-8')

# Example usage
'''
    password = "my_secure_password"
    data = "Hello, this is a secret message!"
    
    # Encrypt
    encrypted = encrypt(data, password)
    print("Encrypted data:", encrypted)

    # Decrypt
    decrypted = decrypt(encrypted, password)
    print("Decrypted data:", decrypted)
'''

# Do doctest if we're run directly
if __name__ == "__main__":
    import doctest

    doctest.testmod()