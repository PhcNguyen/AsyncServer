
# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import os
import pathlib
import lib.customtkinter as ctk

from src.server.utils import InternetProtocol



#          STRUCTURE DATABASE
#  [ DATABASE ]
#      ├─── [ KEY ]
#      │      ├─── public.key
#      │      └─── private.key
#      └─── server.sql


dir_db: str = os.path.join(
    pathlib.Path(__file__).resolve().parent.parent.parent, 
    'database'
)


class UISettings:
    root = ctk.CTk()

    
class NetworkSttings:
    DEBUG: bool = True
    host: str = InternetProtocol.local()
    public: str = InternetProtocol.public()

    port: int = 7272


class DBSettings:
    DEBUG: bool = True
    db_path: str = os.path.join(dir_db, 'server.sql')


class AlgorithmSettings:
    DEBUG: bool = False
    key_path: dict = {
        'public': os.path.join(
            dir_db, 'key', 'public_key.pem'
        ),
        'private': os.path.join(
            dir_db, 'key', 'private_key.pem'
        )
    }