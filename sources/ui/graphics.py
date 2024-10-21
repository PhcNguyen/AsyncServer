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
    def __init__(self, root: ctk.CTk, server: types.TcpServer, subserver: typing.Optional[types.TcpServer] = None):
        super().__init__(root)  # Gọi khởi tạo của lớp cha

        self.current_log = None  # Biến để theo dõi khu vực văn bản hiện tại
        self.cache: FileCache = FileCache()
        self.server: types.TcpServer = server                # Máy chủ đầu tiên
        self.subserver: typing.Optional[types.TcpServer] = subserver  # Máy chủ thứ hai
        self.running: list = [False, False, True]  # Biến để theo dõi trạng thái của server

        # Đăng ký sự kiện đóng cửa sổ
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Khởi tạo vòng lặp sự kiện
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        # Tạo và chạy luồng cho vòng lặp sự kiện
        threading.Thread(target=self.loop.run_forever, daemon=True).start()

    async def _start_server(self):
        try:
            self.start_button.configure(state='disabled')

            # Tạo các tác vụ tự động cập nhật thông tin
            asyncio.create_task(self.auto_log_error())
            asyncio.create_task(self.auto_log_server())

            if not self.server.running:
                asyncio.create_task(self.server.start())

            if self.subserver:
                asyncio.create_task(self.subserver.start())
                self.running[1] = True

            asyncio.create_task(self.auto_updater_info())
            await asyncio.sleep(3.3)
            asyncio.create_task(self.update_server_info())

            if self.server.running:
                self.stop_button.configure(state='normal')
            else:
                self.start_button.configure(state='normal')
                self.stop_button.configure(state='disabled')

        except Exception as e:
            self.log_to_textbox(self.error_log, f"Lỗi khởi động máy chủ: {e}")
            self.start_button.configure(state='normal')
            self.stop_button.configure(state='disabled')

    async def _stop_server(self):
        try:
            self.stop_button.configure(state='disabled')

            if self.server.running:
                await self.server.stop()  # Chạy lệnh dừng server chính

            if self.running[1]:
                await self.subserver.stop()  # Dừng máy chủ thứ hai nếu có
                self.running[1] = False  # Đánh dấu server2 đã dừng

        except Exception as e:
            self.log_to_textbox(self.error_log, f"Lỗi khi dừng máy chủ: {e}")
        finally:
            self.start_button.configure(state='normal')
            await self.update_server_info()


    async def _log(self, cache_file: str, log_target: ctk.CTkTextbox, is_error_log: bool = False):
        """Ghi log ra giao diện."""
        lines = await self.cache.readlines(cache_file)
        if lines:
            for message in lines:
                line_number = self.get_line_number(is_error_log)
                self.log_to_textbox(log_target, self.log_format.format(line_number,TimeUtil.now(),message))
                self.root.update()

    async def _update_log(self, cache_file: str, log_target: ctk.CTkTextbox, is_error_log: bool = False):
        while True:
            if not self.running[2]:
                break

            await self._log(cache_file, log_target, is_error_log)
            await asyncio.sleep(0.00005)  # Chờ trước khi tiếp tục vòng lặp

        await self._log(cache_file, log_target, is_error_log)
        await self.cache.clear_file(cache_file)

    async def update_server_info(self):
        """Cập nhật thông tin server trong giao diện."""
        if self.server.running:
            self.update_label(0, f"{self.server.LOCAL}")
            self.update_label( 1, f"{self.server.PUBLIC}")
        else:
            self.update_label(0, "N/A")
            self.update_label(1, "N/A")

    async def auto_updater_info(self):
        """Cập nhật trạng thái CPU, RAM, Ping và số lượng kết nối định kỳ."""
        while True:
            try:
                if not self.running[2]:
                    self.update_label(2, "N/A")
                    self.update_label(3, "0.0 %")
                    self.update_label(4, "0 MB")
                    self.update_label(5, "0")
                    break  # Dừng vòng lặp nếu server không còn hoạt động

                # Cập nhật thông tin server
                self.update_label(2, f"{InternetProtocol.ping()} ms")
                self.update_label(3, f"{System.cpu()} %")  # Cập nhật giá trị CPU
                self.update_label(4, f"{System.ram()} MB")  # Cập nhật giá trị RAM
                self.update_label(5, "N/A")

                await asyncio.sleep(0.8)  # Chờ trước khi tiếp tục vòng lặp
            except Exception as e:
                print(f"Lỗi xảy ra trong quá trình cập nhật thông tin: {e}")
                await asyncio.sleep(1)  # Cho một khoảng dừng để tránh vòng lặp lỗi nhanh

    async def auto_log_server(self):
        await self._update_log("log-server.cache", self.server_log)

    async def auto_log_error(self):
        await self._update_log("log-error.cache", self.error_log, is_error_log=True)

    def start_server(self):
        """Bắt đầu server với coroutine."""
        asyncio.run_coroutine_threadsafe(self._start_server(), self.loop)

    def stop_server(self) -> None:
        try:
            if not messagebox.askyesno(
                "Thông báo", "Xác nhận dừng máy chủ"
            ): return

            asyncio.run_coroutine_threadsafe(self._stop_server(), self.loop)

        except Exception as e:
            self.log_to_textbox(self.error_log, f"Lỗi khi cố gắng dừng máy chủ: {e}")

    def clear_logs(self):
        if not messagebox.askyesno(
            "Thông báo", "Xác nhận muốn xóa nhật ký?"
        ): return

        self._clear_textbox(self.server_log)
        self._clear_textbox(self.error_log)

    def reload_server(self):
        """Reload server và các thành phần liên quan."""
        if not messagebox.askyesno(
            "Thông báo", "Xác nhận tải lại chương trình?"
        ): return

        if self.server.running:
            self._stop_server()
            self.root.quit()

        System.reset()

    def on_closing(self):
        """Xử lý khi người dùng nhấn nút X để đóng cửa sổ."""
        if self.server.running:
            asyncio.gather(self._stop_server())
            self.running[2] = False

        # Dừng vòng lặp asyncio một cách an toàn
        if self.loop.is_running():
            self.loop.stop()

        self.root.destroy()  # Đóng cửa sổ giao diện
        self.root.quit()

        del self.server
        del self.subserver
        del self.loop
        del self.cache

        # Dọn sạch và thoát chương trình
        System.exit()