
# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import tkinter as tk
import lib.customtkinter as ctk

import asyncio

from datetime import datetime

from . import settings, types
from .settings import InternetProtocol


class Graphics(settings.Graphics):
    def __init__(self, root: ctk.CTk, server: types.Networks):
        self.root = root
        self.server = None
        self.network = server
        
        self.root.title("Server Control")
        self.root.geometry("1200x600")
        self.root.resizable(False, False)
        ctk.set_appearance_mode("dark")  # Đặt chế độ giao diện tối
        ctk.set_default_color_theme("dark-blue")  # Đặt chủ đề màu sắc tối

        # Tạo khung chứa các nút điều khiển
        self.control_frame = ctk.CTkFrame(root)
        self.control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # Nút Start
        self.start_button = ctk.CTkButton(
            self.control_frame,
            text="START",
            command=self.start_server,
            fg_color="#4CAF50",  # Màu nền xanh lá cây
            hover_color="#45a049",  # Màu xanh đậm hơn khi di chuột lên nút
            width=150,
            height=40
        )
        self.start_button.pack(side=tk.LEFT, padx=10)

        # Nút Stop
        self.stop_button = ctk.CTkButton(
            self.control_frame,
            text="STOP",
            command=self.stop_server,
            fg_color="#f44336",  # Màu nền đỏ
            hover_color="#c62828",  # Màu đỏ đậm hơn khi di chuột lên nút
            width=150,
            height=40,
            state='disabled'  # Ban đầu bị vô hiệu hóa
        )
        self.stop_button.pack(side=tk.LEFT, padx=10)

        # Nút Clear
        self.clear_button = ctk.CTkButton(
            self.control_frame,
            text="CLEAR LOGS",
            command=self.clear_logs,
            fg_color="#2196F3",  # Màu nền xanh dương
            hover_color="#1976D2",  # Màu xanh đậm hơn khi di chuột lên nút
            width=150,
            height=40
        )
        self.clear_button.pack(side=tk.LEFT, padx=10)

        # Tạo khung chứa các bản ghi log
        self.log_frame = ctk.CTkFrame(root)
        self.log_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tạo các tab cho bản ghi log
        self.tab_control = ctk.CTkTabview(self.log_frame)
        self.tab_control.add("SERVER")
        self.tab_control.add("ERROR")  
        self.tab_control.pack(expand=1, fill='both')

        # Khu vực văn bản để hiển thị bản ghi kết nối
        self.server_log = ctk.CTkTextbox(
            self.tab_control.tab("SERVER"),
            state='disabled',
            height=20,
            width=100,
            wrap=tk.WORD
        )
        self.server_log.pack(fill=tk.BOTH, expand=True)

        # Khu vực văn bản để hiển thị bản ghi lỗi
        self.error_log = ctk.CTkTextbox(
            self.tab_control.tab("ERROR"),
            state='disabled',
            height=20,
            width=100,
            wrap=tk.WORD
        )
        self.error_log.pack(fill=tk.BOTH, expand=True)

        # Tạo khung chứa thông tin server
        self.info_frame = ctk.CTkFrame(root)
        self.info_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Label và trường hiển thị IP
        self.local_ip = ctk.CTkLabel(self.info_frame, text="Local IP:")
        self.local_ip.grid(row=0, column=0, padx=5, pady=5, sticky='w')  
        self.local_value = ctk.CTkLabel(self.info_frame, text="N/A")
        self.local_value.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        # Label và trường hiển thị Port
        self.public_ip = ctk.CTkLabel(self.info_frame, text="Public IP:")
        self.public_ip.grid(row=1, column=0, padx=5, pady=5, sticky='w') 
        self.public_value = ctk.CTkLabel(self.info_frame, text="N/A")
        self.public_value.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        # Label và trường hiển thị Trạng thái Server
        self.ping_label = ctk.CTkLabel(self.info_frame, text="Ping:")
        self.ping_label.grid(row=2, column=0, padx=5, pady=5, sticky='w')  
        self.ping_value = ctk.CTkLabel(self.info_frame, text="N/A")
        self.ping_value.grid(row=2, column=1, padx=5, pady=5, sticky='w')

    async def start_server(self):
        if self.server:
            self._notify("Server is already running.")
            return
        try:
            self.network.set_message_callback(self.log_message)

            self.server = self.network

            # Start server and ping updater
            asyncio.create_task(self.server.start())
            asyncio.create_task(self._ping_updater())

            # Update button states
            self.start_button.configure(state='disabled')
            self.stop_button.configure(state='normal')

            await self._update_server_info()
        except Exception as e:
            self._notify_error(f"Error starting server: {e}")
            # Re-enable start button if there was an error
            self.start_button.configure(state='normal')

    def stop_server(self):
        if not self.server:
            self._notify("Server is not running.")
            return

        try:
            asyncio.create_task(self.server.stop())
        except Exception as e:
            self._notify_error(f"Error while stopping the server: {e}")
        finally:
            # Reset the server instance
            self.server = None
            self.start_button.configure(state='normal')
            self.stop_button.configure(state='disabled')
            asyncio.create_task(self._update_server_info())

    def clear_logs(self):
        # Xóa nội dung của tất cả các khu vực văn bản
        self._clear_textbox(self.server_log)
        self._clear_textbox(self.error_log)
    
    def log_message(self, message: str):
        """Nhận thông báo từ Networks và phân loại nó để hiển thị đúng tab."""
        if "Notify:" in message:
            self._notify(message.split('Notify:')[-1].strip())
        elif "Error:" in message:
            self._notify_error(message.split('Error:')[-1].strip())
        
        self.root.update()  # Đảm bảo giao diện được cập nhật ngay sau khi log được ghi

    def _clear_textbox(self, textbox):
        """Xóa nội dung của khu vực văn bản."""
        textbox.configure(state='normal')
        textbox.delete(1.0, tk.END)
        textbox.configure(state='disabled')

    def _log_to_textbox(self, textbox, message):
        """Ghi lại thông báo vào khu vực văn bản với thời gian hiện tại."""
        time_stamp = datetime.now().strftime('%d-%m %H:%M:%S')
        formatted_message = f"[{time_stamp}]>  {message}"
        textbox.configure(state='normal')
        textbox.insert(tk.END, f"{formatted_message}\n")
        textbox.configure(state='disabled')
        textbox.yview(tk.END)

    def _notify(self, message):
        """Thông báo về kết nối và ngắt kết nối của client."""
        self._log_to_textbox(self.server_log, message)

    def _notify_error(self, message):
        """Thông báo lỗi."""
        self._log_to_textbox(self.error_log, message)

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
            await asyncio.sleep(0.5)
