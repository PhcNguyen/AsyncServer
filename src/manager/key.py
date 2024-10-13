# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

from src.security import rsa


def isAnotherKeyServer(
    pubic_key: rsa.PublicKey,
    pub_key_server: rsa.PublicKey
) -> bool:
    '''
    pubic_key: Keys saved on the server

    pub_key_server: Server key sends to the user
    '''
    return pub_key_server == pubic_key

'''
def response(
    status: bool, 
    msg: str, 
    number: int = None, 
    coin: int = None
) -> bytes:
    result = {
        'status': status,
        'msg': msg,
        'username': username,
        'password': password,
        **({ 'number': number } if number is not None else {}),
        **({ 'coin': coin } if coin is not None else {})
    }
    return json.dumps(result).encode()'''