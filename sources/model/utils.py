# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import re
import os
import sys
import time
import socket
import typing
import psutil
import os.path
import platform
import requests
import subprocess



class Response:
    @staticmethod
    def success(message: str, **kwargs) -> dict:
        """Trả về dict với trạng thái thành công."""
        response = {"status": True, "message": message}
        response.update(kwargs)
        return response

    @staticmethod
    def error(message: str | Exception, **kwargs) -> dict:
        """Trả về dict với trạng thái lỗi."""
        response = {"status": False, "message": message}
        response.update(kwargs)
        return response


class Colors:
    @staticmethod
    def start(color: str) -> str:
        return f"\033[38;2;{color}m"

    @staticmethod
    def reset() -> str:
        return "\033[0m"

    red = start('255;0;0')
    green = start('0;255;0')
    blue = start('0;0;255')
    white = start('255;255;255')
    black = start('0;0;0')
    gray = start('150;150;150')
    yellow = start('255;255;0')
    purple = start('255;0;255')
    cyan = start('0;255;255')
    orange = start('255;150;0')
    pink = start('255;0;150')
    turquoise = start('0;150;255')


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

    @staticmethod
    def sleep(seconds: float,
            /) -> None:
        time.sleep(seconds)

    @staticmethod
    def dirtory(a: typing.LiteralString | str,
         /,
         *path: (typing.LiteralString | str)
    ) -> (typing.LiteralString | str):
        return os.path.join(a, *path)


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
        except Exception as error:
            print(f"InternetProtocol: {error}")
            return 'N/A'

    @staticmethod
    def public() -> str:
        try:
            response = requests.get("https://api.ipify.org?format=json")
            response.raise_for_status()  # Kiểm tra lỗi HTTP
            ip_data = response.json()
            return ip_data.get("ip")
        except Exception as error:
            print(f"InternetProtocol: {error}")
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
            print(f"InternetProtocol: {error}")
            return 999