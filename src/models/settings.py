# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import os
import pathlib
import tkinter as tk
import lib.customtkinter as ctk

from datetime import datetime
from src.server.utils import InternetProtocol


#          STRUCTURE DATABASE
#  [ DATABASE ]
#      ├─── [ KEY ]
#      │      ├─── public.key
#      │      └─── private.key
#      └─── server.sql


dir_db: str = os.path.join(
    pathlib.Path(__file__).resolve().parent.parent.parent, 
    'database'
)

    
class NetworkSettings:
    """
    Configuration settings for network communication.

    Attributes:
    - DEBUG: Boolean indicating if debug mode is enabled
    - host: Local IP address of the machine
    - public: Public IP address of the machine
    - port: Port number for network communication (default is 7272)
    """
    DEBUG: bool = True
    host: str = InternetProtocol.local()  # Retrieve local IP address
    public: str = InternetProtocol.public()  # Retrieve public IP address
    port: int = 7272  # Default port number


class DBSettings:
    """
    Configuration settings for database connection.

    Attributes:
    - DEBUG: Boolean indicating if debug mode is enabled
    - db_path: Path to the database file (default is 'server.db' in the database directory)
    """
    DEBUG: bool = True
    table_path: str = os.path.join(dir_db, 'table.sql')
    queries_path: str = os.path.join(dir_db, 'queries.sql')
    db_path: str = os.path.join(dir_db, 'server.db')  # Database file path


class AlgorithmSettings:
    """
    Configuration settings for cryptographic algorithms.

    Attributes:
    - DEBUG: Boolean indicating if debug mode is enabled
    - key_path: Dictionary containing paths to public and private key files
    """
    DEBUG: bool = False
    key_path: dict = {
        'public': os.path.join(
            dir_db, 'key', 'public_key.pem'  # Path to the public key
        ),
        'private': os.path.join(
            dir_db, 'key', 'private_key.pem'  # Path to the private key
        )
    }


class UISettings:
    """
    UISettings class to create and manage the user interface for the server application.

    Attributes:
    - root: The main window of the application.
    - control_frame: Frame containing control buttons (START, STOP, CLEAR LOGS).
    - log_frame: Frame for displaying logs (SERVER, ERROR).
    - info_frame: Frame for displaying server information (Local IP, Public IP, Ping).
    """
    
    root = ctk.CTk()

    def __init__(self, root: ctk.CTk):
        self.root = root
        
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

    def clear_logs(self):
        """Xóa nội dung của tất cả các khu vực văn bản."""
        self._clear_textbox(self.server_log)
        self._clear_textbox(self.error_log)

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