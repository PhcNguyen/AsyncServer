# -*- coding: utf-8 -*-
# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import typing
import asyncio
import threading
import customtkinter as ctk
import tkinter.messagebox as messagebox

from sources.utils import types
from sources.configs import UIConfigs
from sources.utils.realtime import TimeUtil
from sources.manager.files.filecache import FileCache
from sources.utils.system import InternetProtocol, System


class Graphics(UIConfigs):
    """Handles the graphical user interface and server management."""

    def __init__(self, root: ctk.CTk, server: types.TcpServer):
        super().__init__(root)
        self.cache: FileCache = FileCache()
        self.server: typing.Optional[types.TcpServer] = server
        self.running = True

        self.root.protocol("WM_DELETE_WINDOW", self.async_command(self.on_closing))

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        threading.Thread(target=self.loop.run_forever, daemon=True).start()

    async def _log(self, cache_file: str, log_target: ctk.CTkTextbox, is_error_log: bool = False):
        """Read and display logs in the specified textbox."""
        lines = await self.cache.read_lines(cache_file)
        if lines:
            for message in lines:
                self.log_to_textbox(
                    log_target, self.log_format.format(self.get_line_number(is_error_log),
                    TimeUtil.now(), message)
                )
            self.root.update()

    async def _update_log(self, cache_file: str, log_target: ctk.CTkTextbox, is_error_log: bool = False):
        """Continuously update logs from the cache file."""
        await self.cache.clear_file(cache_file)
        while self.running:
            await self._log(cache_file, log_target, is_error_log)
            await asyncio.sleep(0.01)  # Delay before the next update

    async def update_server_info(self):
        """Cập nhật thông tin server trong giao diện."""
        ip0_info = f"{self.server.LOCAL if self.running else 'N/A'}"
        ip1_info = f"{self.server.PUBLIC if self.running else 'N/A'}"
        self.update_label(0, ip0_info)
        self.update_label(1, ip1_info)

    async def auto_updater_info(self):
        """Cập nhật trạng thái CPU, RAM, Ping và số lượng kết nối định kỳ."""
        while self.running:
            try:
                self.update_label(2, f"{InternetProtocol.ping()} ms")
                self.update_label(3, f"{System.cpu()} %")
                self.update_label(4, f"{System.ram()} MB")
                self.update_label(5, f"{self.server.current_connections}")
                await asyncio.sleep(0.2)
            except Exception as e:
                print(f"Lỗi xảy ra trong quá trình cập nhật thông tin: {e}")
                await asyncio.sleep(0.8)

    async def auto_log_server(self):
        await self._update_log("log-server.cache", self.server_log)

    async def auto_log_error(self):
        await self._update_log("log-error.cache", self.error_log, is_error_log=True)

    async def start_server(self):
        """Starts the server asynchronously and manages log updates."""
        self.update_start_button(False)

        asyncio.create_task(self.auto_log_error())
        asyncio.create_task(self.auto_log_server())

        if not self.server.running:
            asyncio.create_task(self.server.start())

        await asyncio.sleep(3.3)
        asyncio.create_task(self.auto_updater_info())
        asyncio.create_task(self.update_server_info())

        self.update_stop_button(True)

    async def stop_server(self) -> None:
        if not messagebox.askyesno("Thông báo", "Xác nhận dừng máy chủ"): return

        self.update_stop_button(False)

        if self.server.running:
            await self.server.stop()

        await self.update_server_info()

        self.update_start_button(True)

    async def clear_logs(self):
        if not messagebox.askyesno("Thông báo", "Xác nhận muốn xóa nhật ký?"): return
        self._clear_textbox(self.server_log)
        self._clear_textbox(self.error_log)

    async def reload_server(self):
        """Reload server và các thành phần liên quan."""
        if not messagebox.askyesno("Thông báo", "Xác nhận tải lại chương trình?"): return

        if self.server.running:
            await self.stop_server()
            self.root.quit()
        System.reset()

    async def on_closing(self):
        """Handle window close event asynchronously."""
        self.running = False  # Stop any running loops or updates

        try:
            if self.server.running:
                # Stop the server asynchronously
                stop_future = asyncio.run_coroutine_threadsafe(self.stop_server(), self.loop)
                stop_future.result()  # Wait for stop_server() to finish

            if self.loop.is_running():
                self.loop.stop()

            # Safely stop any updates or interaction with the widgets
            if self.root:
                self.root.quit()
                self.root.destroy()

            self.cache.clear()

            System.exit()

        except Exception as e:
            print(f"Error during on_closing: {e}")