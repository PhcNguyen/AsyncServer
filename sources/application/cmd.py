# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.



class Cmd:
    """
    This class defines various command types used in the application.

    Constants:
    - LOGIN: Command for user login
    - LOGOUT: Command for user logout
    - REGISTER: Command for user registration
    - PLAYER_INFO: Command to retrieve player information
    - PUBLIC_KEY_INFO: Command to retrieve public key information

    - UPDATE_APPELLARION: Command to update player's appellation
    - UPDATE_COIN: Command to update player's coin balance
    - TRANSFER_COINS: Command to transfer coins between players
    """
    
    LOGIN = 0
    LOGOUT = 1
    REGISTER = 2
    PLAYER_INFO = 3
    PUBLIC_KEY_INFO = 4

    UPDATE_APPELLARION = 5
    UPDATE_COIN = 6
    TRANSFER_COINS = 7