# -*- coding: utf-8 -*-
# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import typing
import asyncio
import datetime
import threading
import customtkinter as ctk
import tkinter.messagebox as messagebox

from sources.utils import types
from sources.configs import UIConfigs
from sources.manager.files.filecache import FileCache
from sources.utils.system import InternetProtocol, System



class Graphics(UIConfigs):
    def __init__(self, root: ctk.CTk, server: types.TcpServer, second_server: typing.Optional[types.TcpServer] = None):
        super().__init__(root)  # Gọi khởi tạo của lớp cha

        self.current_log = None  # Biến để theo dõi khu vực văn bản hiện tại
        self.cache: FileCache = FileCache()
        self.server: typing.Optional[types.TcpServer] = server                # Máy chủ đầu tiên
        self.second_server: typing.Optional[types.TcpServer | None] = second_server  # Máy chủ thứ hai

        # Biến để theo dõi trạng thái của server
        self.srv1_running  = False
        self.srv2_running  = False

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

            await self.update_server_infor()

            # Tạo các tác vụ tự động cập nhật thông tin
            asyncio.create_task(self.auto_log_error())
            asyncio.create_task(self.auto_log_server())
            asyncio.create_task(self.auto_updater_infor())

            # Chạy máy chủ chính
            if self.server:
                self.srv1_running = True  # Đánh dấu server1 đang chạy
                asyncio.create_task(self.server.start())  # Khởi động server chính

            # Chạy máy chủ thứ hai nếu có
            if self.second_server:
                self.srv2_running = True  # Đánh dấu server2 đang chạy
                asyncio.create_task(self.second_server.start())  # Khởi động server thứ hai

            self.stop_button.configure(state='normal')

        except Exception as e:
            self.log_to_textbox(self.error_log, f"Lỗi khởi động máy chủ: {e}")
            self.start_button.configure(state='normal')
            self.stop_button.configure(state='disabled')

    async def _stop_server(self):
        try:
            self.stop_button.configure(state='disabled')

            if self.srv1_running:
                await self.server.stop()         # Chạy lệnh dừng server chính
                self.srv1_running = False        # Đánh dấu server1 đã dừng

            if self.srv2_running:
                await self.second_server.stop()  # Dừng máy chủ thứ hai nếu có
                self.srv2_running = False        # Đánh dấu server2 đã dừng

        except Exception as e:
            self.log_to_textbox(self.error_log, f"Lỗi khi dừng máy chủ: {e}")
        finally:
            await self.update_server_infor()
            self.start_button.configure(state='normal')

    async def _log(self, cache_file: str, log_target: ctk.CTkTextbox, is_error_log: bool = False):
        lines = await self.cache.readlines(cache_file)
        if lines:
            for message in lines:
                if is_error_log:
                    self.error_line += 1
                    target_line = self.error_line
                else:
                    self.server_line += 1
                    target_line = self.server_line

                self.log_to_textbox(log_target, self.log_format.format(
                    target_line,
                    datetime.datetime.now().strftime("%d/%m %H:%M:%S"),
                    message
                ))
                self.root.update()

    async def _update_log(self, cache_file: str, log_target: ctk.CTkTextbox, is_error_log: bool = False):
        while True:
            if not self.srv1_running and not self.srv2_running:
                break

            await self._log(cache_file, log_target, is_error_log)
            await asyncio.sleep(0.005)  # Chờ trước khi tiếp tục vòng lặp

        await self._log(cache_file, log_target, is_error_log)
        await self.cache.clear_file(cache_file)

    async def update_server_infor(self):
        """Cập nhật thông tin server trong giao diện."""
        if self.server:
            self.local_value.configure(text=InternetProtocol.local())
            self.public_value.configure(text=InternetProtocol.public())
        else:
            self.local_value.configure(text="N/A")
            self.public_value.configure(text="N/A")

    async def auto_updater_infor(self):
        """Cập nhật trạng thái CPU, RAM, Ping và số lượng kết nối định kỳ."""
        while True:
            # Kiểm tra xem server có còn hoạt động hay không
            if not self.srv1_running and not self.srv2_running :
                self.ping_value.configure(text="N/A")
                self.cpu_value.configure(text="0.0 %")
                self.ram_value.configure(text="0 MB")
                self.connections_value.configure(text="0")
                break  # Dừng vòng lặp nếu server không còn hoạt động

            # Cập nhật thông tin server
            self.ping_value.configure(text=f"{InternetProtocol.ping()} ms")
            self.cpu_value.configure(text=f"{System.cpu()} %")  # Cập nhật giá trị CPU
            self.ram_value.configure(text=f"{System.ram()} MB")  # Cập nhật giá trị RAM
            self.connections_value.configure(text=f"N/A")

            await asyncio.sleep(0.8)  # Chờ trước khi tiếp tục vòng lặp

    async def auto_log_server(self):
        await self._update_log("log-server.cache", self.server_log)

    async def auto_log_error(self):
        await self._update_log("log-error.cache", self.error_log, is_error_log=True)

    def start_server(self):
        if self.srv1_running  or self.srv2_running :
            self.log_to_textbox(self.server_log, "Máy chủ đang hoạt động")
            return

        """Bắt đầu server với coroutine."""
        asyncio.run_coroutine_threadsafe(self._start_server(), self.loop)

    def stop_server(self) -> None:
        if not self.srv1_running  and not self.srv2_running :
            self.log_to_textbox(self.server_log, "Máy chủ không hoạt động")
            return

        try:
            asyncio.run_coroutine_threadsafe(self._stop_server(), self.loop)
        except Exception as e:
            self.log_to_textbox(self.error_log, f"Lỗi khi cố gắng dừng máy chủ: {e}")

    def clear_logs(self):
        """Xóa nội dung của tất cả các khu vực văn bản."""
        self._clear_textbox(self.server_log)
        self._clear_textbox(self.error_log)

    def reload_server(self):
        """Reload server và các thành phần liên quan."""
        confirm = messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn tải lại server không?")

        if confirm:
            if self.srv1_running  or self.srv2_running :
                self.stop_server()  # Dừng server nếu đang chạy
                self.root.quit()

            System.reset()

    def on_closing(self):
        """Xử lý khi người dùng nhấn nút X để đóng cửa sổ."""
        if self.srv1_running  or self.srv2_running :
            try:
                # Chạy coroutine stop_server và chờ nó hoàn thành
                self.stop_server()
            except Exception as e:
                print(f"Lỗi dừng máy chủ: {e}")

        # Dừng vòng lặp asyncio một cách an toàn
        if self.loop.is_running():
            self.loop.stop()

        self.root.destroy()  # Đóng cửa sổ giao diện
        self.root.quit()

        del self

        # Dọn sạch và thoát chương trình
        System.exit()