
import os
import typing
import pathlib
import tkinter as tk
import customtkinter as ctk

from PIL import Image
from customtkinter import CTkImage
from sources.model.utils import System

BASE_DIR: str = str(pathlib.Path(__file__).resolve().parent.parent.parent)
DIR_FONT = os.path.join(BASE_DIR, "resource", "font")
DIR_ICON = os.path.join(BASE_DIR, "resource", "icon")



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

        UIConfigs.load_font(
            font_path=System.dirtory(DIR_FONT, 'JetBrainsMono-Italic-VariableFont_wght.ttf'),
            font_name='JetBrainsMono-Italic-VariableFont'
        )
        UIConfigs.load_font(
            font_path=System.dirtory(DIR_FONT, 'JetBrainsMono-VariableFont_wght.ttf'),
            font_name='JetBrainsMono-VariableFont'
        )

        self.root = root

        self.server_line = 0
        self.error_line = 0

        self.log_format = "[ {:05d} | {:<12} ]> {}"

        self.root.title("Server Control")
        self.root.geometry("1200x620")
        self.root.resizable(width=False, height=False)
        self.root.iconbitmap(System.dirtory(DIR_ICON, '0.ico'))

        ctk.set_appearance_mode("dark")  # Đặt chế độ giao diện tối
        ctk.set_default_color_theme("dark-blue")  # Đặt chủ đề màu sắc tối

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

        self._setup_server_tab()
        self._setup_error_tab()
        self._setup_buttons()
        self._setup_labels()

    def start_server(self):
        ...

    def stop_server(self):
        ...

    def clear_logs(self):
        ...

    def reload_server(self):
        ...

    @staticmethod
    def load_font(font_path, font_name) -> None:
        # Load the font and return a CTkFont object
        tk.font.Font(family=font_path, name=font_name)

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

    def _setup_buttons(self):
        # Tải ảnh PNG sử dụng Pillow (PIL)
        start_image = ctk.CTkImage(
            Image.open(System.dirtory(DIR_ICON, '1.png')), size=(20, 20)
        )
        stop_image = ctk.CTkImage(
            Image.open(System.dirtory(DIR_ICON, '2.png')), size=(20, 20)
        )
        clear_image = ctk.CTkImage(
            Image.open(System.dirtory(DIR_ICON, '3.png')), size=(20, 20)
        )
        reload_image = ctk.CTkImage(
            Image.open(System.dirtory(DIR_ICON, '9.png')), size=(20, 20)
        )

        # Nút Start
        self.start_button = ctk.CTkButton(
            self.control_frame,
            text="Start",
            command=self.start_server,
            fg_color="#4CAF50",  # Màu nền xanh lá cây
            hover_color="#45a049",  # Màu xanh đậm hơn khi di chuột lên nút
            width=150,
            height=40,
            image=start_image,
            font=('JetBrainsMono-VariableFont', 13)
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
            state='disabled',  # Ban đầu bị vô hiệu hóa
            image=stop_image,
            font=('JetBrainsMono-VariableFont', 13)
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
            height=40,
            image=clear_image,
            font=('JetBrainsMono-VariableFont', 13)
        )
        self.clear_button.pack(side=tk.LEFT, padx=10)

        # Nút Reload
        self.reload_button = ctk.CTkButton(
            self.control_frame,
            text="Reload",
            command=self.reload_server,
            fg_color="#FFC107",  # Màu vàng
            hover_color="#ffca28",  # Màu vàng đậm hơn khi di chuột
            width=150,
            height=40,
            image=reload_image,
            font=('JetBrainsMono-VariableFont', 13)
        )
        self.reload_button.pack(side=tk.LEFT, padx=10)

    def _setup_server_tab(self):
        # Khu vực văn bản để hiển thị bản ghi server
        self.server_log = ctk.CTkTextbox(
            self.tab_control.tab("   Server   "),
            state='disabled',  # Đặt ban đầu là disabled
            height=20,
            width=100,
            wrap=tk.WORD,
            fg_color="#000000",  # Màu chữ (white)
            bg_color="#000000",  # Màu nền (black)
            font=('JetBrainsMono-VariableFont', 16)
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
            font=('JetBrainsMono-VariableFont', 16)
        )
        self.error_log.pack(fill=tk.BOTH, expand=True)

    def _setup_labels(self):
        # Define font sizes
        variable_font_size = 14
        italic_font_size = 14

        # Tạo khung cha chứa thông tin server
        self.info_container = ctk.CTkFrame(self.root)
        self.info_container.pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=8)

        # Tạo khung chứa thông tin server
        self.info_frame = ctk.CTkFrame(self.info_container)
        self.info_frame.pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=8, expand=True)

        # Tạo khung chứa thông tin bổ sung
        self.info_frame2 = ctk.CTkFrame(self.info_container)
        self.info_frame2.pack(side=tk.LEFT, fill=tk.Y, expand=True, padx=8, pady=8)

        # Label và trường hiển thị IP với font tuỳ chỉnh
        self.local_ip = self.create_label(
            self.info_frame, " Local IP:",
            ('JetBrainsMono-VariableFont', variable_font_size), 0, 0,
            System.dirtory(DIR_ICON, '4.png')
        )
        self.local_value = self.create_label(
            self.info_frame, "N/A",
            ('JetBrainsMono-VariableFont', italic_font_size), 0, 1
        )

        self.public_ip = self.create_label(
            self.info_frame, " Public IP:",
            ('JetBrainsMono-VariableFont', variable_font_size), 1, 0,
            System.dirtory(DIR_ICON, '4.png')
        )
        self.public_value = self.create_label(
            self.info_frame, "N/A",
            ('JetBrainsMono-VariableFont', italic_font_size),
            1, 1, sticky='e'
        )

        self.ping_label = self.create_label(
            self.info_frame, " Ping:",
            ('JetBrainsMono-VariableFont', variable_font_size), 2, 0,
            System.dirtory(DIR_ICON, '5.png')
        )
        self.ping_value = self.create_label(
            self.info_frame, "N/A",
            ('JetBrainsMono-VariableFont', italic_font_size),
            2, 1, sticky='e'
        )

        # Add new labels for CPU, RAM, and Connections with font tuỳ chỉnh
        self.cpu_label = self.create_label(
            self.info_frame2, " CPU:",
            ('JetBrainsMono-VariableFont', variable_font_size), 0, 0,
            System.dirtory(DIR_ICON, '6.png')
        )
        self.cpu_value = self.create_label(
            self.info_frame2, "N/A",
            ('JetBrainsMono-VariableFont', italic_font_size), 0, 1
        )

        self.ram_label = self.create_label(
            self.info_frame2, " RAM:",
            ('JetBrainsMono-VariableFont', variable_font_size), 1, 0,
            System.dirtory(DIR_ICON, '7.png')
        )
        self.ram_value = self.create_label(
            self.info_frame2, "N/A",
            ('JetBrainsMono-VariableFont', italic_font_size), 1, 1
        )

        self.connections_label = self.create_label(
            self.info_frame2, " Connections:",
            ('JetBrainsMono-VariableFont', variable_font_size), 2, 0,
            System.dirtory(DIR_ICON, '8.png')
        )
        self.connections_value = self.create_label(
            self.info_frame2, "0",
            ('JetBrainsMono-VariableFont', italic_font_size), 2, 1
        )