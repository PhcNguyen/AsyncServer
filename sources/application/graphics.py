# -*- coding: utf-8 -*-
# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import typing
import asyncio
import threading
import customtkinter as ctk

from sources.model import types
from sources.manager.cache import Cache
from sources.model.realtime import Realtime
from sources.application.configs import UIConfigs
from sources.application.utils import InternetProtocol, System



class Graphics(UIConfigs):
    def __init__(self, root: ctk.CTk, server: types.AsyncNetworks):
        super().__init__(root)  # Gọi khởi tạo của lớp cha

        self.current_log = None  # Biến để theo dõi khu vực văn bản hiện tại
        self.cache: Cache = Cache()
        self.server: typing.Optional[types.AsyncNetworks] = None
        self.network: types.AsyncNetworks = server

        # Đăng ký sự kiện đóng cửa sổ
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Khởi tạo vòng lặp sự kiện
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        # Tạo và chạy luồng cho vòng lặp sự kiện
        threading.Thread(target=self.loop.run_forever, daemon=True).start()
          
    async def _start_server(self):
        if self.server:
            self.log_to_textbox(self.server_log, "Server is already running.")
            return
        try:
            self.server = self.network
            self.start_button.configure(state='disabled')

            asyncio.create_task(self._auto_updater_infor())
            asyncio.create_task(self._auto_updater_message())

            await asyncio.gather(
                self._update_server_infor(),
                return_exceptions = True  # Ensures exceptions are returned without halting execution
            )
            # Chạy _auto_updater dưới nền mà không chặn các tác vụ khác
            asyncio.create_task(self.server.start())

            self.stop_button.configure(state='normal')

        except Exception as e:
            self.log_to_textbox(self.error_log, f"Error starting server: {e}")
            self.start_button.configure(state='normal')
            self.stop_button.configure(state='disabled')
    
    async def _stop_server(self):
        if self.server:
            try:
                self.stop_button.configure(state='disabled')

                await self.server.stop()  # Chạy lệnh dừng server
                # self._log_to_textbox(self.server_log, "Server stopped successfully.")
            except Exception as e:
                self.log_to_textbox(self.error_log, f"Error while stopping the server: {e}")
            finally:
                self.server = None
                await self._update_server_infor()
                self.start_button.configure(state='normal')
    
    async def _update_server_infor(self):
        """Cập nhật thông tin server trong giao diện."""        
        if self.server:
            self.local_value.configure(text=InternetProtocol.local())
            self.public_value.configure(text=InternetProtocol.public())
        else:
            self.local_value.configure(text="N/A")
            self.public_value.configure(text="N/A")


    async def _auto_updater_infor(self):
        """Cập nhật trạng thái CPU, RAM, Ping và số lượng kết nối định kỳ."""
        while True:
            # Kiểm tra xem server có còn hoạt động hay không
            if not self.server:
                self.ping_value.configure(text="N/A")

                self.cpu_value.configure(text="0.0 %")
                self.ram_value.configure(text="0 MB")
                self.connections_value.configure(text="0")
                break  # Dừng vòng lặp nếu server không còn hoạt động

            # Cập nhật thông tin server
            self.ping_value.configure(text=f"{InternetProtocol.ping()} ms")
            self.cpu_value.configure(text=f"{System.cpu()} %")  # Cập nhật giá trị CPU
            self.ram_value.configure(text=f"{System.ram()} MB")  # Cập nhật giá trị RAM
            self.connections_value.configure(text=f"{self.server.active_client()}")

            await asyncio.sleep(0.8)  # Chờ trước khi tiếp tục vòng lặp

    async def _auto_updater_message(self):
        while True:
            # Check if the server is still running
            if not self.server:
                break

            # Read lines from cache and process them if not empty
            lines = await self.cache.read_lines()
            if lines:
                for line in lines:
                    await self.log_message(line)

            await asyncio.sleep(0.3)  # Wait before continuing the loop

        # Once the server is stopped, process remaining cache and clear it
        lines = await self.cache.read_lines()
        if lines:
            for line in lines:
                await self.log_message(line)

        await self.cache.clear()

    def start_server(self):
        if self.server:
            self.log_to_textbox(self.server_log, "Server is already running.")
            return

        """Bắt đầu server với coroutine."""
        asyncio.run_coroutine_threadsafe(self._start_server(), self.loop)

    def stop_server(self) -> None:
        if not self.server:
            self.log_to_textbox(self.server_log, "Server is not running.")
            return

        try:
            asyncio.run_coroutine_threadsafe(self._stop_server(), self.loop)
        except Exception as e:
            self.log_to_textbox(self.error_log, f"Error while trying to stop the server: {e}")

    async def log_message(self, message: str | int | typing.Any):
        """Nhận thông báo từ Networks, ... và phân loại nó để hiển thị đúng tab."""
        message_type, actual_message = self.parse_message(message)

        if message_type == "Notify":
            self.server_line += 1
            log_target = self.server_log
        elif message_type == "Error":
            self.error_line += 1
            log_target = self.error_log
        else:
            return  # Không xử lý nếu không phải Notify hoặc Error

        self.log_to_textbox(log_target, self.log_format.format(
            self.server_line,
            Realtime.now().strftime("%d/%m %H:%M:%S"),
            actual_message
        ))

        self.root.update()
    
    def clear_logs(self):
        """Xóa nội dung của tất cả các khu vực văn bản."""
        self._clear_textbox(self.server_log)
        self._clear_textbox(self.error_log)

    def on_closing(self):
        """Xử lý khi người dùng nhấn nút X để đóng cửa sổ."""
        if self.server:
            try:
                # Chạy coroutine stop_server và chờ nó hoàn thành
                self.loop.run_until_complete(self.stop_server())
            except Exception as e:
                print(f"Error stopping server: {e}")

        # Dừng vòng lặp asyncio một cách an toàn
        if self.loop.is_running():
            self.loop.stop()

        self.root.destroy()  # Đóng cửa sổ giao diện

        # Dọn sạch và thoát chương trình
        # System.clear()
        System.exit()