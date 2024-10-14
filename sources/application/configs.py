# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import os
import pathlib
import tkinter as tk
import customtkinter as ctk

from sources.application.utils import InternetProtocol


DIR_DB: str = os.path.join(
    pathlib.Path(__file__).resolve().parent.parent.parent, 
    'database'
)



class Configs:
    
    class Network:
        """
        Configuration settings for network communication.

        Attributes:
        - DEBUG: Boolean indicating if debug mode is enabled
        - local: Local IP address of the machine
        - public: Public IP address of the machine
        - port: Port number for network communication (default is 7272)
        """
        DEBUG: bool = False
        local: str = InternetProtocol.local()  # Retrieve local IP address
        public: str = InternetProtocol.public()  # Retrieve public IP address
        port: int = 7272  # Default port number

        DIR_DATA = os.path.join(DIR_DB, 'data')

        block_file = os.path.join(DIR_DATA, 'block.txt')

    class DirPath:
        """
        Configuration settings for cryptographic algorithms.

        Attributes:
        - DEBUG: Boolean indicating if debug mode is enabled
        - key_path: Dictionary containing paths to public and private key files
        """

        
        DIR_KEY = os.path.join(DIR_DB, 'key')
        DIR_DATA = os.path.join(DIR_DB, 'data')

        table_path: str = os.path.join(DIR_DB, 'table.sql')
        queries_path: str = os.path.join(DIR_DB, 'queries.sql')
        db_path: str = os.path.join(DIR_DB, 'server.db')  # Database file path

        key_path = {
            "public": os.path.join(DIR_KEY, "public.key"),
            "private": os.path.join(DIR_KEY, "private.key")
        }
        


class UIConfigs:
    """
    UIConfigs class to create and manage the user interface for the server application.

    Attributes:
    - root: The main window of the application.
    - control_frame: Frame containing control buttons (START, STOP, CLEAR LOGS).
    - log_frame: Frame for displaying logs (SERVER, ERROR).
    - info_frame: Frame for displaying server information (Local IP, Public IP, Ping).
    """
    
    root = ctk.CTk()

    def __init__(self, root: ctk.CTk):
        self.root = root

        self.server_line = 0
        self.error_line = 0
        
        # Khởi tạo khung chứa các nút điều khiển
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

        # Tạo khung cha chứa thông tin server
        self.info_container = ctk.CTkFrame(root)
        self.info_container.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Tạo khung chứa thông tin server
        self.info_frame = ctk.CTkFrame(self.info_container)
        self.info_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Tạo khung chứa thông tin bổ sung
        self.info_frame2 = ctk.CTkFrame(self.info_container)
        self.info_frame2.pack(side=tk.LEFT, fill=tk.Y, expand=True, padx=10, pady=10)

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

        # Add new labels for CPU, RAM, and Connections
        self.cpu_label = ctk.CTkLabel(self.info_frame2, text="CPU:")
        self.cpu_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')

        self.cpu_value = ctk.CTkLabel(self.info_frame2, text="N/A")
        self.cpu_value.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        self.ram_label = ctk.CTkLabel(self.info_frame2, text="RAM:")
        self.ram_label.grid(row=1, column=0, padx=5, pady=5, sticky='w')

        self.ram_value = ctk.CTkLabel(self.info_frame2, text="N/A")
        self.ram_value.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        self.connections_label = ctk.CTkLabel(self.info_frame2, text="Connections:")
        self.connections_label.grid(row=2, column=0, padx=5, pady=5, sticky='w')

        self.connections_value = ctk.CTkLabel(self.info_frame2, text="0")
        self.connections_value.grid(row=2, column=1, padx=5, pady=5, sticky='w')
    
    def _clear_textbox(self, textbox: ctk.CTkTextbox):
        """Xóa nội dung của khu vực văn bản."""
        textbox.configure(state='normal')
        textbox.delete(1.0, tk.END)
        textbox.configure(state='disabled')
    
    def _log_to_textbox(
        self, 
        textbox: ctk.CTkTextbox, 
        message: str, 
        text_color: str = "white"
    ):
        """Append a message to the specified textbox with optional text color.""" 
        textbox.configure(state='normal')  # Cho phép chỉnh sửa
        textbox.insert('end', message + "\n")  # Chèn thông điệp vào cuối khu vực văn bản
        textbox.tag_add('color_tag', 'end-1c linestart', 'end-1c lineend')  # Đánh dấu dòng cuối cùng để thay đổi màu
        textbox.tag_config('color_tag', foreground=text_color)  # Thiết lập màu sắc cho văn bản
        
        textbox.configure(state='disabled')  # Vô hiệu hóa chỉnh sửa lại
        textbox.yview('end')  # Cuộn xuống cuối khu vực văn bản