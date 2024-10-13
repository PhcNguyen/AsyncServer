# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import re
import os
import sys
import socket
import typing
import platform
import requests
import subprocess


class Colors:
    @staticmethod
    def start(color: str) -> str: 
        return f"\033[38;2;{color}m"

    red = start.__func__('255;0;0')
    green = start.__func__('0;255;0')
    blue = start.__func__('0;0;255')
    white = start.__func__('255;255;255')
    black = start.__func__('0;0;0')
    gray = start.__func__('150;150;150')
    yellow = start.__func__('255;255;0')
    purple = start.__func__('255;0;255')
    cyan = start.__func__('0;255;255')
    orange = start.__func__('255;150;0')
    pink = start.__func__('255;0;150')
    turquoise = start.__func__('0;150;255')


class System:
    """
    4 functions: 
    - clear()   |   Clears the terminal screen
    - command() |   Executes a system command
    - reset()   |   Resets the Python script by re-executing it
    - exit()    |   Exits the Python script
    """

    Windows = os.name == 'nt'

    @staticmethod
    def clear() -> int:
        return os.system(
            "cls" if System.Windows else "clear"
        )
        
    @staticmethod
    def command(command: str) -> int:
        return os.system(command)

    @staticmethod
    def reset() -> typing.NoReturn:
        return os.execv(
            sys.executable, ['python'] + sys.argv
        )

    @staticmethod
    def exit() -> typing.NoReturn:
        sys.exit()


class InternetProtocol:
    @staticmethod
    def local() -> str:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))  # Kết nối đến một máy chủ DNS công cộng
                ip_address = s.getsockname()[0]  # Lấy địa chỉ IP của máy tính
            return ip_address
        except Exception as e:
            return 'N/A'

    @staticmethod
    def public() -> str:
        try:
            response = requests.get("https://api.ipify.org?format=json")
            response.raise_for_status()  # Kiểm tra lỗi HTTP
            ip_data = response.json()
            return ip_data.get("ip")
        except Exception as e:
            return 'N/A'
    
    @staticmethod
    def ping() -> (int | str):
        # Xác định lệnh ping dựa trên hệ điều hành
        host = "google.com"
        param = "-n" if platform.system().lower() == "windows" else "-c"
        
        try:
            # Thực hiện lệnh ping
            output = subprocess.check_output(["ping", param, "1", host], universal_newlines=True)
            
            # Phân tích đầu ra để tìm thời gian ping
            if platform.system().lower() == "windows":
                # Tìm thời gian từ Reply from
                match = re.search(r'time=(\d+)ms', output)
                if match:
                    return match.group(1)  # Trả về thời gian ping
            else:
                # Unix-based: Tìm thời gian trong chuỗi kết quả
                match = re.search(r'time[=<](\d+\.?\d*) ms', output)
                if match:
                    return match.group(1)  # Trả về thời gian ping
            
            return 'N/A'
        except subprocess.CalledProcessError:
            return 'N/A'