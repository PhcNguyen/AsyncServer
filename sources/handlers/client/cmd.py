# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

from enum import Enum



class Cmd(Enum):
    LOGIN = 0
    LOGOUT = 1
    REGISTER = 2
    PLAYER_INFO = 3

    UPDATE_APPELLATION = 4
    UPDATE_COIN = 5
    TRANSFER_COINS = 6