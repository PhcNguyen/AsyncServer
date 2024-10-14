# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import re
import os
import sys
import socket
import typing
import psutil
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
    6 functions: 
    - clear()   |   Clears the terminal screen
    - command() |   Executes a system command
    - reset()   |   Resets the Python script by re-executing it
    - exit()    |   Exits the Python script
    - cpu()     |   Returns the current CPU usage percentage.
    - ram()     |   Returns the current RAM usage percentage.
    """

    Windows = os.name == 'nt'

    @staticmethod
    def clear() -> int:
        return os.system(
            "cls" if System.Windows else "clear"
        )
        
    @staticmethod
    def command(command: str) -> int:
        print("Application is command...")
        return os.system(command)

    @staticmethod
    def reset() -> typing.NoReturn:
        print("Application is reset...")
        return os.execv(
            sys.executable, ['python'] + sys.argv
        )

    @staticmethod
    def exit() -> typing.NoReturn:
        print("Application is closing...")
        sys.exit()
    
    @staticmethod
    def cpu():
        """Trả về tỷ lệ sử dụng CPU."""
        return psutil.cpu_percent(interval=1)

    @staticmethod
    def ram():
        """Trả về tỷ lệ sử dụng RAM."""
        return psutil.virtual_memory().percent


class InternetProtocol:
    """
    2 variables:
    - host: The address of the server to ping (default is google.com)
    - param: The parameter for the ping command, depending on the operating system

    3 functions:
    - local()   |   Retrieves the local IP address of the machine
    - public()  |   Retrieves the public IP address from an external service
    - ping()    |   Executes a ping command to the host and returns the response time
    """

    # Xác định lệnh ping dựa trên hệ điều hành
    param = "-n" if platform.system().lower() == "windows" else "-c"
    host = "google.com"

    @staticmethod
    def local() -> str:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))  # Kết nối đến một máy chủ DNS công cộng
                ip_address = s.getsockname()[0]  # Lấy địa chỉ IP của máy tính
            return ip_address
        except Exception:
            return 'N/A'

    @staticmethod
    def public() -> str:
        try:
            response = requests.get("https://api.ipify.org?format=json")
            response.raise_for_status()  # Kiểm tra lỗi HTTP
            ip_data = response.json()
            return ip_data.get("ip")
        except Exception:
            return 'N/A'
    
    @staticmethod
    def ping(timeout: int = 1) -> (int | str):
        try:
            # Sử dụng lệnh ping với timeout
            output = subprocess.check_output(
                ["ping", InternetProtocol.param, str(timeout), InternetProtocol.host], 
                universal_newlines=True
            )
            
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
            
            return 999
        except (subprocess.CalledProcessError, Exception) as error:
            return 999