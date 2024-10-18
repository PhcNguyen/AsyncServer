# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import os
import pathlib

BASE_DIR: str = str(pathlib.Path(__file__).resolve().parent.parent.parent)

# Đường dẫn đến các thư mục
DIR_DB = os.path.join(BASE_DIR, "database")
DIR_RES = os.path.join(BASE_DIR, "resource")

# Đường dẫn đến các thư mục con
DIR_SQL = os.path.join(DIR_DB, "sql")
DIR_LOG = os.path.join(DIR_DB, "log")
DIR_KEY = os.path.join(DIR_DB, "key")
DIR_DATA = os.path.join(DIR_DB, "data")
DIR_CACHE = os.path.join(DIR_DB, "cache")

DIR_ICON = os.path.join(DIR_RES, "icon")
DIR_FONT = os.path.join(DIR_RES, "font")


def file_paths(file_name: str, dir_type: str = "database") -> str:
    directory = file_name.split(".")[-1].lower()
    base_dir = DIR_DB if dir_type == "database" else DIR_RES

    dir_map = {
        "pem": "key", "db": "sql", "txt": "data", "json": "data",
        "yaml": "data", "csv": "data", "log": "logs", "ini": "config",
        "xml": "config", "md": "docs"
    }

    directory = dir_map.get(base_dir, directory)

    if not os.path.exists(os.path.join(base_dir, directory)):
        os.makedirs(os.path.join(base_dir, directory))

    return os.path.join(base_dir, directory, file_name)