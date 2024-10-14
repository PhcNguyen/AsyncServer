# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import asyncio
import threading
import customtkinter as ctk

from sources.model.realtime import Realtime
from sources.model.types import NetworksTypes
from sources.application.configs import UIConfigs
from sources.application.utils import InternetProtocol, System



class Graphics(UIConfigs):
    def __init__(self, root: ctk.CTk, server: NetworksTypes):
        super().__init__(root)  # Gọi khởi tạo của lớp cha
        self.server = None
        self.network = server

        self.current_log = None  # Biến để theo dõi khu vực văn bản hiện tại

        self.root.title("Server Control")
        self.root.geometry("1200x620")
        self.root.resizable(False, False)
        ctk.set_appearance_mode("dark")  # Đặt chế độ giao diện tối
        ctk.set_default_color_theme("dark-blue")  # Đặt chủ đề màu sắc tối

        # Đăng ký sự kiện đóng cửa sổ
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Khởi tạo vòng lặp sự kiện
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        # Tạo và chạy luồng cho vòng lặp sự kiện
        threading.Thread(target=self.loop.run_forever, daemon=True).start()
          
    async def _start_server(self):
        if self.server:
            self._log_to_textbox(self.server_log, "Server is already running.")
            return
        try:
            self.network.set_message_callback(self.log_message)
            self.server = self.network

            self.start_button.configure(state='disabled')
            self.stop_button.configure(state='normal')

            await asyncio.gather(
                self.server.start(),
                self._auto_updater(),
                self._update_server_info(),
            )
        except Exception as e:
            self._log_to_textbox(self.error_log, f"Error starting server: {e}")
            self.start_button.configure(state='normal')
    
    async def _stop_server(self):
        if self.server:
            try:
                await self.server.stop()  # Chạy lệnh dừng server
                # self._log_to_textbox(self.server_log, "Server stopped successfully.")
            except Exception as e:
                self._log_to_textbox(self.error_log, f"Error while stopping the server: {e}")
            finally:
                self.server = None
                self.start_button.configure(state='normal')
                self.stop_button.configure(state='disabled')
                await self._update_server_info()
    
    async def _update_server_info(self):
        """Cập nhật thông tin server trong giao diện."""        
        if self.server:
            self.local_value.configure(text=InternetProtocol.local())
            self.public_value.configure(text=InternetProtocol.public())
            self.ping_value.configure(text=f"{InternetProtocol.ping()} ms")

            self.cpu_value.configure(text=f"{System.cpu()} %") 
            self.ram_value.configure(text=f"{System.ram()} MB")
            self.connections_value.configure(text=f"{self.server.active_client()}")
        else:
            self.local_value.configure(text="N/A")
            self.public_value.configure(text="N/A")
            self.ping_value.configure(text="N/A")

            self.cpu_value.configure(text="0.0 %") 
            self.ram_value.configure(text="0 MB")
            self.connections_value.configure(text="0")

    async def _auto_updater(self):
        """Cập nhật trạng thái CPU, RAM, Ping và số lượng kết nối định kỳ."""
        while True:
            # Kiểm tra xem server có còn hoạt động hay không
            if not self.server:
                break  # Dừng vòng lặp nếu server không còn hoạt động

            # Cập nhật thông tin server
            self.ping_value.configure(text=f"{InternetProtocol.ping()} ms")
            self.cpu_value.configure(text=f"{System.cpu()} %")  # Cập nhật giá trị CPU
            self.ram_value.configure(text=f"{System.ram()} MB")  # Cập nhật giá trị RAM
            self.connections_value.configure(text=f"{self.server.active_client()}")

            await asyncio.sleep(0.8)  # Chờ trước khi tiếp tục vòng lặp


    def start_server(self):
        if self.server:
            self._log_to_textbox(self.server_log, "Server is already running.")
            return

        """Bắt đầu server với coroutine."""
        asyncio.run_coroutine_threadsafe(self._start_server(), self.loop)

    def stop_server(self):
        if not self.server:
            self._log_to_textbox(self.server_log, "Server is not running.")
            return

        try:
            asyncio.run_coroutine_threadsafe(self._stop_server(), self.loop)
        except Exception as e:
            self._log_to_textbox(self.error_log, f"Error while trying to stop the server: {e}")

    def log_message(self, message: str):
        """Nhận thông báo từ Networks, ... và phân loại nó để hiển thị đúng tab."""
        if "Notify:" in message:
            self.server_line += 1  
            
            self._log_to_textbox(self.server_log, self.log_format.format(
                self.server_line,                     # Adjusted to have a fixed width
                Realtime.now("%d/%m %H:%M:%S"),       # Adjusted to have a fixed width for time
                message.split('Notify:')[-1].strip()  # The actual message
            ))
        elif "Error:" in message:
            self.error_line += 1  
            
            self._log_to_textbox(self.error_log, self.log_format.format(
                self.server_line,
                Realtime.now("%d/%m %H:%M:%S"), 
                message.split('Error:')[-1].strip()
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
                asyncio.run_coroutine_threadsafe(self.stop_server(), self.loop)
            except Exception as e:
                print(f"Error stopping server: {e}")

        self.loop.stop()     # Dừng vòng lặp asyncio
        self.root.destroy()  # Đóng cửa sổ giao diện

        System.clear()       # Dọn sạch màn hình
        System.exit()        # Thoát chương trình