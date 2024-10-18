# -*- coding: utf-8 -*-
# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import typing
import asyncio
import threading

from sources.model import types
from sources.manager.files.filecache import FileCache
from sources.model.utils import InternetProtocol, System, Colors



class Terminal:
    def __init__(self, server: types.TcpServer):
        self.server: typing.Optional[types.TcpServer] = None
        self.cache: FileCache = FileCache()
        self.network: types.TcpServer = server

        # Khởi tạo vòng lặp sự kiện
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        # Tạo và chạy luồng cho vòng lặp sự kiện
        threading.Thread(target=self.loop.run_forever, daemon=True).start()

    async def _start_server(self):
        if self.server:
            print(f"{Colors.red}Server is already running.{Colors.white}")
            return

        try:
            self.server = self.network
            self.status_server()

            # Tạo các tác vụ tự động cập nhật thông tin
            asyncio.create_task(self._auto_updater_message())
            asyncio.create_task(self.server.start())

            print(f"{Colors.green}Server started successfully.{Colors.white}")

        except Exception as e:
            print(f"{Colors.red}Error starting server: {e}{Colors.white}")

    async def _stop_server(self):
        if self.server:
            try:
                await self.server.stop()  # Chạy lệnh dừng server
                print(f"{Colors.green}Server stopped successfully.{Colors.white}")
            except Exception as e:
                print(f"{Colors.red}Error while stopping the server: {e}{Colors.white}")
            finally:
                self.server = None

    async def _auto_updater_message(self):
        while True:
            if not self.server:
                break

            lines = await self.cache.read_lines()
            if lines:
                for line in lines:
                    print(f"{line}")

            await asyncio.sleep(0.5)  # Chờ trước khi tiếp tục vòng lặp

        lines = await self.cache.read_lines()
        if lines:
            for line in lines:
                print(f"{line}")

        await self.cache.clear_file()

    def start_server(self):
        if self.server:
            print(f"{Colors.red}Server is already running.{Colors.white}")
            return

        """Bắt đầu server với coroutine."""
        asyncio.run_coroutine_threadsafe(self._start_server(), self.loop)

    def stop_server(self):
        if not self.server:
            print(f"{Colors.red}Server is not running.{Colors.white}")
            return

        try:
            asyncio.run_coroutine_threadsafe(self._stop_server(), self.loop)
        except Exception as e:
            print(f"{Colors.red}Error while trying to stop the server: {e}{Colors.white}")

    def status_server(self):
        """Cập nhật thông tin server trên terminal."""
        if self.server:
            print(f"Local IP: {InternetProtocol.local()}")
            print(f"Public IP: {InternetProtocol.public()}")
            print(f"CPU Usage: {System.cpu()} %")
            print(f"RAM Usage: {System.ram()} MB")
        else:
            print(f"{Colors.red}Server is not running.{Colors.white}")

    def on_closing(self):
        """Đóng server một cách an toàn."""
        if self.server:
            try:
                self.loop.run_until_complete(self.stop_server())
            except Exception as e:
                print(f"{Colors.red}Error stopping server: {e}{Colors.white}")

        # Dừng vòng lặp asyncio
        if self.loop.is_running():
            self.loop.stop()

        print(f"{Colors.red}Exiting program.{Colors.white}")
        System.exit()

def mainloop(terminal_server: Terminal):
    """Hàm này cho phép người dùng nhập lệnh để điều khiển server."""
    System.clear()
    print(f"{Colors.red}Chương trình đang khởi động vui lòng đợi 10-20s !{Colors.white}")
    print("Command ({}start{}/{}status{}/{}stop{}/{}exit{}/help)".format(
        Colors.green, Colors.white,
        Colors.blue, Colors.white,
        Colors.yellow, Colors.white,
        Colors.red, Colors.white
    ))
    command = input("Enter command: " ).strip().lower()

    while True:
        if command == "start":
            terminal_server.start_server()

        elif command == "status":
            terminal_server.status_server()

        elif command == "stop":
            terminal_server.stop_server()

        elif command == "exit":
            terminal_server.stop_server()
            terminal_server.on_closing()
            break
        elif command == "":
            pass
        elif command == "help":
            print(f"--- Hướng dẫn sử dụng ---")
            print(f"{Colors.green}start: {Colors.white}Khởi động server.")
            print(f"{Colors.blue}status: {Colors.white}Xem thông tin trạng thái của server.")
            print(f"{Colors.yellow}stop: {Colors.white}Dừng server.")
            print(f"{Colors.red}exit: {Colors.white}Thoát khỏi chương trình.")
        else:

            print(f"{Colors.red}Unknown command. Please enter 'start', 'status', 'stop', 'exit', or 'help'.{Colors.white}")

        command = input().strip().lower()