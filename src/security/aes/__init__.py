# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified TUDL License.

from aes import (
    generate_key,
    encrypt,
    decrypt
)

__author__ = "PhcNguyen"
__date__ = "2024-10-13"
__version__ = "1.0.31"

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

__all__ = [
    "aes"
]