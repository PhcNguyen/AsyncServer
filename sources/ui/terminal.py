# -*- coding: utf-8 -*-
# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import typing
import asyncio
import threading

from sources.utils import types
from sources.manager.files.filecache import FileCache
from sources.utils.system import InternetProtocol, System, Colors



class Terminal:
    def __init__(self, server: types.TcpServer):
        self.server: typing.Optional[types.TcpServer] = None
        self.cache = FileCache()
        self.network = server
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        threading.Thread(target=self.loop.run_forever, daemon=True).start()

    async def _auto_updater(self):
        """Updates messages from the cache and server status."""
        while self.server:
            lines = await self.cache.read_lines()
            print("\n".join(lines) if lines else "")
            await asyncio.sleep(0.5)

        await self.cache.clear_file()

    def start_server(self):
        """Starts the server and message updater."""
        if self.server:
            print(f"{Colors.red}Server is already running.{Colors.white}")
            return

        self.server = self.network
        asyncio.create_task(self._auto_updater())
        asyncio.create_task(self.server.start())
        print(f"{Colors.green}Server started successfully.{Colors.white}")

    def stop_server(self):
        """Stops the server."""
        if self.server:
            asyncio.run_coroutine_threadsafe(self.server.stop(), self.loop)
            print(f"{Colors.green}Server stopped successfully.{Colors.white}")
            self.server = None
        else:
            print(f"{Colors.red}Server is not running.{Colors.white}")

    def status_server(self):
        """Displays server status."""
        if self.server:
            print(
                f"Local IP: {InternetProtocol.local()}\n"
                f"Public IP: {InternetProtocol.public()}\n"
                f"CPU Usage: {System.cpu()}%\n"
                f"RAM Usage: {System.ram()}MB"
            )
        else:
            print(f"{Colors.red}Server is not running.{Colors.white}")

    def on_closing(self):
        """Safely shuts down the server and exits."""
        self.stop_server()
        if self.loop.is_running():
            self.loop.stop()
        print(f"{Colors.red}Exiting program.{Colors.white}")
        System.exit()

    @staticmethod
    def mainloop(terminal_server):
        """Handles user input for server control."""
        System.clear()
        print(f"{Colors.red}Chương trình đang khởi động vui lòng đợi 10-20s !{Colors.white}")
        print("Commands: start, status, stop, exit, help")

        commands = {
            "start": terminal_server.start_server,
            "status": terminal_server.status_server,
            "stop": terminal_server.stop_server,
            "exit": lambda: (terminal_server.stop_server(), terminal_server.on_closing())
        }

        while True:
            command = input("Enter command: ").strip().lower()
            if command in commands:
                commands[command]()
            elif command == "help":
                print("Commands: start, status, stop, exit")
            else:
                print(f"{Colors.red}Unknown command.{Colors.white}")