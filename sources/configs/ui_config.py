# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import os
import typing
import pathlib
import asyncio
import tkinter as tk
import customtkinter as ctk
import tkinter.messagebox as messagebox

from PIL import Image
from customtkinter import CTkImage
from sources.utils.system import System


BASE_DIR: str = str(pathlib.Path(__file__).resolve().parent.parent.parent)
DIR_FONT = os.path.join(BASE_DIR, "resource", "font")
DIR_ICON = os.path.join(BASE_DIR, "resource", "icon", "graphics")


class UIConfigs:
    root = ctk.CTk()

    def __init__(self, root: ctk.CTk):
        self.labels = []
        self.root = root

        self.server_line = 0
        self.error_line = 0

        self.loop = asyncio.new_event_loop()
        self.log_format = "[ {:05d} | {:<12} ]> {}"

        self._initialize_ui()

    def _initialize_ui(self):
        self._configure_window()
        self._create_frames()

        self._load_fonts()
        self._setup_tabs()

        self._setup_buttons()
        self._setup_labels()

    @staticmethod
    def _load_fonts():
        """Load required fonts for the application."""
        for font_file, font_name in [
            ('JetBrainsMono-Italic-VariableFont_wght.ttf', 'JetBrainsMono-Italic-VariableFont'),
            ('JetBrainsMono-VariableFont_wght.ttf', 'JetBrainsMono-VariableFont')
        ]:
            tk.font.Font(family=System.paths(DIR_FONT, font_file), name=font_name)

    def get_line_number(self, is_error_log: bool):
        """Lấy số dòng hiện tại cho log."""
        if is_error_log: self.error_line += 1; return self.error_line
        else: self.server_line += 1; return self.server_line

    @staticmethod
    def log_to_textbox(
            textbox: ctk.CTkTextbox,
            message: str | int | typing.Any,
            text_color: str = "white"
    ):
        """Append a message to the specified textbox with optional text color."""
        textbox.configure(state='normal')  # Cho phép chỉnh sửa
        textbox.insert('end', message + "\n")  # Chèn thông điệp vào cuối khu vực văn bản
        textbox.tag_add('color_tag', 'end-1c linestart', 'end-1c lineend')  # Đánh dấu dòng cuối cùng để thay đổi màu
        textbox.tag_config('color_tag', foreground=text_color)  # Thiết lập màu sắc cho văn bản

        textbox.configure(state='disabled')  # Vô hiệu hóa chỉnh sửa lại
        textbox.yview('end')  # Cuộn xuống cuối khu vực văn bản

    @staticmethod
    def ask_confirmation(message: str) -> bool:
        """Display a confirmation dialog and return the user's response."""
        return messagebox.askyesno("Thông báo", message)

    @staticmethod
    def _create_textbox(parent):
        textbox = ctk.CTkTextbox(
            parent,
            state='disabled',
            height=20,
            width=100,
            wrap=tk.WORD,
            fg_color="#000000",
            font=('JetBrainsMono-VariableFont', 16)
        )
        textbox.pack(fill=tk.BOTH, expand=True)
        return textbox

    @staticmethod
    def create_label(frame, text, font, row, column, icon_path=None, sticky='w'):
        image = None
        if icon_path:
            # Tải icon từ file
            icon = Image.open(icon_path)
            icon = icon.resize((17, 17), Image.Resampling.LANCZOS)  # Điều chỉnh kích thước icon nếu cần
            image = CTkImage(icon)  # Sử dụng CTkImage thay vì ImageTk.PhotoImage

        label = ctk.CTkLabel(frame, text=text, font=font, image=image, compound="left")
        label.grid(row=row, column=column, padx=5, pady=5, sticky=sticky)

        label.image = image  # Giữ tham chiếu đến hình ảnh
        return label

    def _configure_window(self):
        self.root.title("Server Management")
        self.root.geometry("1180x620")
        self.root.resizable(False, False)
        self.root.iconbitmap(System.paths(DIR_ICON, '0.ico'))
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

    def _create_frames(self):
        self.control_frame = ctk.CTkFrame(self.root)
        self.control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        self.log_frame = ctk.CTkFrame(self.root)
        self.log_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _setup_buttons(self):
        self.start_button = self.create_button(
            "Start", self.async_command(self.start_server),
            "#4CAF50", "#45a049", '1.png'
        )
        self.stop_button = self.create_button(
            "Stop", self.async_command(self.stop_server),
            "#f44336", "#c62828", '2.png', state='disabled'
        )
        self.clear_button = self.create_button(
            "Clear log", self.async_command(self.clear_logs),
            "#000000", "#424242", '3.png'
        )
        self.reload_button = self.create_button(
            "Reload", self.async_command(self.reload_server),
            "#000000", "#424242", '9.png'
        )

    def _setup_tabs(self):
        self.tab_control = ctk.CTkTabview(self.log_frame)
        self.tab_control.add("   Server   ")
        self.tab_control.add("   Error    ")
        self.tab_control.pack(expand=True, fill='both')
        self._setup_server_tab()
        self._setup_error_tab()

    def _setup_server_tab(self):
        self.server_log = self._create_textbox(
            self.tab_control.tab("   Server   ")
        )

    def _setup_error_tab(self):
        self.error_log = self._create_textbox(
            self.tab_control.tab("   Error    ")
        )

    def create_button(self, text, command, color, hover_color, image_file, state='normal'):
        image = ctk.CTkImage(Image.open(System.paths(DIR_ICON, image_file)), size=(20, 20))
        button = ctk.CTkButton(
            self.control_frame,
            text=text,
            command=command,
            fg_color=color,
            hover_color=hover_color,
            width=150,
            height=40,
            image=image,
            font=('JetBrainsMono-VariableFont', 13),
            state=state
        )
        button.pack(side=tk.LEFT, padx=10)
        return button

    def async_command(self, func):
        """Helper to run an async function in the event loop."""
        return lambda: asyncio.run_coroutine_threadsafe(func(), self.loop)

    def _setup_labels(self):
        self.info_frame = ctk.CTkFrame(self.root)
        self.info_frame.pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=8)

        labels = [
            ("  Local  ", "N/A", '4.png'),
            ("  Public ", "N/A", '4.png'),
            ("  Ping   ", "N/A", '5.png')
        ]
        for idx, (text, value, icon) in enumerate(labels):
            label, value_label = self._create_label(self.info_frame, text, value, icon, idx)
            self.labels.append((label, value_label))

        self.info_frame2 = ctk.CTkFrame(self.root)
        self.info_frame2.pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=8)

        resource_labels = [
            ("  CPU     ", "N/A", '6.png'),
            ("  RAM     ", "N/A", '7.png'),
            ("  Connect ", "0", '8.png')
        ]
        for idx, (text, value, icon) in enumerate(resource_labels):
            label, value_label = self._create_label(self.info_frame2, text, value, icon, idx)
            self.labels.append((label, value_label))

    @staticmethod
    def _create_label(frame, text, value, icon, row):
        label_font = ('JetBrainsMono-VariableFont', 14)
        value_font = ('JetBrainsMono-VariableFont', 12)
        label = ctk.CTkLabel(frame, text=text, font=label_font)
        value_label = ctk.CTkLabel(frame, text=value, font=value_font)

        icon_path = System.paths(DIR_ICON, icon)
        UIConfigs.create_label(frame, text, label_font, row, 0, icon_path, sticky='w')

        value_label.grid(row=row, column=1, padx=5, pady=5, sticky='w')
        return label, value_label

    def update_label(self, index: int, new_value: str):
        """Cập nhật giá trị của nhãn tại index."""
        if 0 <= index < len(self.labels):
            self.labels[index][1].configure(text=new_value)  # Cập nhật nhãn giá trị

    def _clear_textbox(self, textbox: ctk.CTkTextbox):
        """Xóa nội dung của khu vực văn bản với hiệu ứng xóa nhanh dần."""
        self.server_line = 0
        self.error_line = 0

        self.clear_button.configure(state='disabled')
        textbox.configure(state='normal')  # Chuyển trạng thái về 'normal' để xóa nội dung

        textbox_content = textbox.get("1.0", "end")  # Lấy toàn bộ nội dung của textbox
        lines = textbox_content.splitlines()  # Chia nội dung thành từng dòng

        # Hiệu ứng xóa nhanh dần từ dưới lên
        delay = 0.05  # Bắt đầu với độ trễ lớn hơn
        for i in range(len(lines)):
            textbox.delete(f"{len(lines) - i}.0", f"{len(lines) - i}.end")  # Xóa từng dòng từ dưới lên
            self.root.update()  # Cập nhật giao diện để hiển thị hiệu ứng xóa
            System.sleep(delay)  # Điều chỉnh tốc độ tại đây
            delay = max(0.001, delay * 0.7)  # Giảm dần độ trễ để xóa nhanh hơn

        textbox.delete("1.0", "end")  # Đảm bảo xóa hết nội dung sau hiệu ứng
        self.root.update()

        textbox.configure(state='disabled')  # Đặt lại trạng thái về 'disabled'
        self.clear_button.configure(state='normal')

    def update_start_button(self, state):
        self.start_button.configure(state="normal" if state else "disabled")

    def update_stop_button(self, state):
        self.stop_button.configure(state="normal" if state else "disabled")

    async def start_server(self):...
    async def stop_server(self):...
    async def clear_logs(self): ...
    async def reload_server(self): ...