
# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import os
import pathlib
import customtkinter as ctk

from .utils import InternetProtocol



class Graphics:
    root = ctk.CTk()

    
class Networks:
    host: str = InternetProtocol.local()
    public: str = InternetProtocol.public()

    port: int = 7272


class DatabaseManager:
    db_path: str = os.path.join(
        pathlib.Path(__file__).resolve().parent.parent, 
        'database',
        'server.sql'
    )