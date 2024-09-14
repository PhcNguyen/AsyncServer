
# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

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


class MySqlite:
    db_path: str = 'services/db/database.sql' 