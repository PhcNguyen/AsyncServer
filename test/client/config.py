# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import os
import platform


def create_file_conf(
    files: str,
    ip_address = "192.168.1.2", 
    port = 7272,
) -> None:
    if not os.path.exists(files):
        with open(files) as conf_file:
            conf_file.write(f"IP={ip_address}\n")
            conf_file.write(f"Port={port}\n")

def get_data_dir():
    if platform.system() == "Windows":
        return os.path.join(os.getenv('LOCALAPPDATA'))
    elif platform.system() == "Darwin":
        return os.path.join(os.path.expanduser('~'), 'Library', 'Application Support')
    else:
        return os.path.join(os.path.expanduser('~'), '.config')


DIR = get_data_dir()
CRAPS = os.path.join(DIR, "CRAPS")
KEY_DIR = os.path.join(CRAPS, "keys")


os.makedirs(CRAPS, exist_ok=True)
os.makedirs(KEY_DIR, exist_ok=True)
create_file_conf(os.path.join(CRAPS, "network.conf"))


class ConfigClient:
    key_path = {
        "public": os.path.join(KEY_DIR, "public_key.pem"),
        "private": os.path.join(KEY_DIR, "private_key.pem")
    }

    @staticmethod
    def network_config() -> list[str, int]:
        config = {}
        if os.path.exists(os.path.join(CRAPS, "network.conf")):
            with open(os.path.join(CRAPS, "network.conf"), 'r') as conf_file:
                for line in conf_file:
                    key, value = line.strip().split('=')
                    config[key] = value
        host: str = config.get("IP", "127.0.0.1")
        port: int = config.get("Port", 7272)
        return [host, port]