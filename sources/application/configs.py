# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import os
import typing
import pathlib
import tkinter as tk
import customtkinter as ctk

from sources.application.utils import InternetProtocol, System


DIR_DB: str = os.path.join(
    pathlib.Path(__file__).resolve().parent.parent.parent, 
    'database'
)



class Configs:
    
    class Network:
        """
        Configuration settings for network communication.

        Attributes:
        - DEBUG (bool): Indicates if debug mode is enabled.
        - local (str): Local IP address of the machine.
        - public (str): Public IP address of the machine.
        - port (int): Port number for network communication (default is 7272).
        - DIR_DATA (str): Directory path for data storage.

        """
        DEBUG: bool = False
        local: str = InternetProtocol.local()  # Retrieve local IP address
        public: str = InternetProtocol.public()  # Retrieve public IP address
        port: int = 7272  # Default port number

        DIR_DATA = os.path.join(DIR_DB, 'data')

    class DirPath:
        """
        Configuration settings for cryptographic algorithms and database paths.

        Attributes:
        - DIR_KEY (str): Directory path for key storage.
        - DIR_DATA (str): Directory path for data storage.
        - table_path (str): Path to the SQL table file.
        - queries_path (str): Path to the SQL queries file.
        - db_path (str): Path to the database file.
        - key_path (dict): Dictionary containing paths to public and private key files.
        - block_file (str): Path to the block file.
        """
        
        DIR_KEY = os.path.join(DIR_DB, 'key')
        DIR_DATA = os.path.join(DIR_DB, 'data')

        table_path: str = os.path.join(DIR_DB, 'table.sql')
        queries_path: str = os.path.join(DIR_DB, 'queries.sql')
        db_path: str = os.path.join(DIR_DB, 'server.db')  # Database file path

        key_path = {
            "public": os.path.join(DIR_KEY, "public_key.pem"),
            "private": os.path.join(DIR_KEY, "private_key.pem")
        }

        cache_file = os.path.join(DIR_DB, 'cache')
        block_file = os.path.join(DIR_DATA, 'block.txt')



class UIConfigs:
    """
    UIConfigs class to create and manage the user interface for the server application.

    Attributes:
    - root (ctk.CTk): The main window of the application.
    - control_frame (ctk.CTkFrame): Frame containing control buttons (START, STOP, CLEAR LOGS).
    - log_frame (ctk.CTkFrame): Frame for displaying logs (SERVER, ERROR).
    - info_frame (ctk.CTkFrame): Frame for displaying server information (Local IP, Public IP, Ping).
    - info_frame2 (ctk.CTkFrame): Frame for displaying additional server information (CPU, RAM, Connections).
    - server_log (ctk.CTkTextbox): Text area for displaying server logs.
    - error_log (ctk.CTkTextbox): Text area for displaying error logs.
    - local_value (ctk.CTkLabel): Label showing the local IP address.
    - public_value (ctk.CTkLabel): Label showing the public IP address.
    - ping_value (ctk.CTkLabel): Label showing the ping status.
    - cpu_value (ctk.CTkLabel): Label showing the CPU usage.
    - ram_value (ctk.CTkLabel): Label showing the RAM usage.
    - connections_value (ctk.CTkLabel): Label showing the number of connections.
    """
    
    root = ctk.CTk()

    def __init__(self, root: ctk.CTk):
        self.root = root

        self.server_line = 0
        self.error_line = 0

        self.log_format = "[ {:05d} | {:<12} ]> {}"
        
        # Khởi tạo khung chứa các nút điều khiển
        self.control_frame = ctk.CTkFrame(root)
        self.control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # Tạo khung chứa các bản ghi log
        self.log_frame = ctk.CTkFrame(root)
        self.log_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tạo các tab cho bản ghi log
        self.tab_control = ctk.CTkTabview(self.log_frame)
        self.tab_control.add("   Server   ")
        self.tab_control.add("   Error    ")
        self.tab_control.pack(expand=1, fill='both')

        # Khu vực văn bản để hiển thị bản ghi kết nối

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

        self._setup_server_tab()
        self._setup_error_tab()
        self._setup_buttons()

    def start_server(self): ...
    def stop_server(self): ...
    def clear_logs(self): ...

    def _clear_textbox(self, textbox: ctk.CTkTextbox):
        """Xóa nội dung của khu vực văn bản."""
        self.server_line = 0
        self.error_line = 0

        self.clear_button.configure(state='disabled')
        textbox.configure(state='normal')  # Chuyển trạng thái về 'normal' để xóa nội dung
        for i in range(100, -1, -5):  # Thay đổi từ 100% đến 0%
            # Tạo mã màu hex cho độ mờ
            color = f'#{i:02x}{i:02x}{i:02x}'  # Màu xám với độ mờ
            textbox.configure(fg_color=color)  # Thay đổi màu văn bản
            self.root.update()  # Cập nhật giao diện
            System.sleep(0.005)  # Thay đổi tốc độ tại đây

        textbox.delete("1.0", "end")  # Xóa nội dung sau khi hiệu ứng hoàn thành
        self.root.update()
        textbox.configure(state='disabled')  # Đặt lại trạng thái về 'disabled'
        self.clear_button.configure(state='normal')

    @staticmethod
    def _log_to_textbox(
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

    def _setup_buttons(self):
        # Nút Start
        self.start_button = ctk.CTkButton(
            self.control_frame,
            text="Start",
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
            text="Stop",
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
            text="Clear logs",
            command=self.clear_logs,
            fg_color="#2196F3",  # Màu nền xanh dương
            hover_color="#1976D2",  # Màu xanh đậm hơn khi di chuột lên nút
            width=150,
            height=40
        )
        self.clear_button.pack(side=tk.LEFT, padx=10)

    def _setup_server_tab(self):
        # Khu vực văn bản để hiển thị bản ghi server
        self.server_log = ctk.CTkTextbox(
            self.tab_control.tab("   Server   "),
            state='disabled',  # Đặt ban đầu là disabled
            height=20,
            width=100,
            wrap=tk.WORD,
            fg_color="#000000",  # Màu chữ (white)
            bg_color="#000000"  # Màu nền (black)
        )
        self.server_log.pack(fill=tk.BOTH, expand=True)

    def _setup_error_tab(self):
        # Khu vực văn bản để hiển thị bản ghi lỗi
        self.error_log = ctk.CTkTextbox(
            self.tab_control.tab("   Error    "),
            state='disabled',  # Đặt ban đầu là disabled
            height=20,
            width=100,
            wrap=tk.WORD,
            fg_color="#000000",  # Màu chữ (white)
            bg_color="#000000",  # Màu nền (light red)
        )
        self.error_log.pack(fill=tk.BOTH, expand=True)