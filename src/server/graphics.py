# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import asyncio
import threading
import customtkinter as ctk

from src.server.utils import System
from src.models.types import NetworksTypes
from src.models.settings import UISettings
from src.server.utils import InternetProtocol


class Graphics(UISettings):
    def __init__(self, root: ctk.CTk, server: NetworksTypes):
        super().__init__(root)  # Gọi khởi tạo của lớp cha
        self.server = None
        self.network = server

        self.current_log = None  # Biến để theo dõi khu vực văn bản hiện tại

        self.root.title("Server Control")
        self.root.geometry("1200x600")
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

    def start_server(self):
        if self.server:
            return
        
        """Bắt đầu server với coroutine."""
        asyncio.run_coroutine_threadsafe(self._start_server(), self.loop)

    def stop_server(self):
        if not self.server:
            self._log_to_textbox(self.server_log, "Server is not running.")
            return

        try:
            # Gọi hàm dừng server từ luồng asyncio
            asyncio.run_coroutine_threadsafe(self._stop_server(), self.loop)
        except Exception as e:
            self._log_to_textbox(self.error_log, f"Error while trying to stop the server: {e}")

    def log_message(self, message: str):
        """Nhận thông báo từ Networks và phân loại nó để hiển thị đúng tab."""
        if "Notify:" in message:
            self._log_to_textbox(self.server_log, message.split('Notify:')[-1].strip())
        elif "Error:" in message:
            self._log_to_textbox(self.error_log, message.split('Error:')[-1].strip())
        else:
            self._log_to_textbox(self.server_log, f"Unknown message: {message}")

        self.root.update()  # Đảm bảo giao diện được cập nhật ngay sau khi log được ghi
    
    def on_closing(self):
        """Xử lý khi người dùng nhấn nút X để đóng cửa sổ."""
        if self.server:
            try:
                asyncio.run_coroutine_threadsafe(self.stop_server(), self.loop)  # Dừng server nếu đang chạy
            except Exception as e:
                print(f"Error stopping server: {e}")

        self.loop.stop()     # Dừng vòng lặp asyncio
        self.root.destroy()  # Đóng cửa sổ giao diện

        print("Application is closing...")  # Thông báo cho biết ứng dụng đang đóng
        System.exit()                       # Thoát chương trình

    async def _update_server_info(self):
        """Cập nhật thông tin server trong giao diện."""        
        if self.server:
            self.local_value.configure(text=InternetProtocol.local())
            self.public_value.configure(text=InternetProtocol.public())
            self.ping_value.configure(text=f"{InternetProtocol.ping()} ms")
        else:
            self.local_value.configure(text="N/A")
            self.public_value.configure(text="N/A")
            self.ping_value.configure(text="N/A")

    async def _ping_updater(self):
        """Cập nhật trạng thái ping định kỳ."""        
        while self.server:
            self.ping_value.configure(text=f"{InternetProtocol.ping()} ms")
            await asyncio.sleep(0.8)  # Cập nhật mỗi 0.8 giây
    
    async def _start_server(self):
        if self.server:
            # self._log_to_textbox(self.server_log, "Server is already running.")
            return
        try:
            self.network.set_message_callback(self.log_message)
            self.server = self.network

            self.start_button.configure(state='disabled')
            self.stop_button.configure(state='normal')

            await asyncio.gather(
                self.server.start(), # Đảm bảo đây là coroutine
                self._update_server_info(),
                self._ping_updater(),      
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
                await self._update_server_info()  # Cập nhật thông tin sau khi dừng server