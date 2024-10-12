
# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import os
import pathlib
import customtkinter as ctk

from models.utils import InternetProtocol



class Graphics:
    root = ctk.CTk()

    
class Networks:
    host: str = InternetProtocol.local()
    public: str = InternetProtocol.public()

    port: int = 7272


class Postgres:
    user: str = "postgres"
    host: str = 'localhost'
    port: int = 5432

    dbname: str = "postgres"
    password: str = "postgres"


class DatabaseManager:
    db_path: str = os.path.join(
        pathlib.Path(__file__).resolve().parent.parent, 
        'services',
        'database.sql'
    )