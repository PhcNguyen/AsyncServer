import customtkinter as ctk
import socket
import json

# Hàm gửi dữ liệu đến server
def send_data(action, **kwargs):
    data = {"action": action}
    data.update(kwargs)
    client_socket.send(json.dumps(data).encode())
    response = client_socket.recv(1024).decode()
    return json.loads(response)

# Hàm xử lý sự kiện đăng ký
def register():
    username = username_entry.get()
    password = password_entry.get()
    if not username or not password:
        ctk.CTkMessageBox.show_warning("Input Error", "Username and password are required.")
        return
    response = send_data("register", username=username, password=password)
    ctk.CTkMessageBox.show_info("Register", response["message"])

# Hàm xử lý sự kiện đăng nhập
def login():
    username = username_entry.get()
    password = password_entry.get()
    if not username or not password:
        ctk.CTkMessageBox.show_warning("Input Error", "Username and password are required.")
        return
    response = send_data("login", username=username, password=password)
    if response["status"] == "success":
        ctk.CTkMessageBox.show_info("Login", response["message"])
        login_frame.pack_forget()
        chat_frame.pack(fill=ctk.BOTH, expand=True)
    else:
        ctk.CTkMessageBox.show_error("Login Failed", response["message"])

# Hàm gửi tin nhắn
def send_message():
    sender = username_entry.get()
    receiver = receiver_entry.get()
    message = message_entry.get()
    if not receiver or not message:
        ctk.CTkMessageBox.show_warning("Input Error", "Receiver and message are required.")
        return
    response = send_data("message", sender=sender, receiver=receiver, message=message)
    ctk.CTkMessageBox.show_info("Message Status", response["message"])

# Hàm gửi yêu cầu kết bạn
def send_friend_request():
    sender = username_entry.get()
    receiver = friend_request_entry.get()
    if not receiver:
        ctk.CTkMessageBox.show_warning("Input Error", "Receiver is required.")
        return
    response = send_data("friend_request", sender=sender, receiver=receiver)
    ctk.CTkMessageBox.show_info("Friend Request Status", response["message"])

# Hàm chấp nhận yêu cầu kết bạn
def accept_friend_request():
    sender = username_entry.get()
    friend = accept_friend_entry.get()
    if not friend:
        ctk.CTkMessageBox.show_warning("Input Error", "Friend is required.")
        return
    response = send_data("accept_friend", sender=sender, friend=friend)
    ctk.CTkMessageBox.show_info("Accept Friend Status", response["message"])

# Hàm block người dùng
def block_user():
    blocker = username_entry.get()
    blockee = block_user_entry.get()
    if not blockee:
        ctk.CTkMessageBox.show_warning("Input Error", "User to block is required.")
        return
    response = send_data("block", blocker=blocker, blockee=blockee)
    ctk.CTkMessageBox.show_info("Block Status", response["message"])

# Tạo cửa sổ chính
app = ctk.CTk()
app.title("Chat Client")

# Cài đặt giao diện đăng nhập/đăng ký
login_frame = ctk.CTkFrame(app)
login_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)

ctk.CTkLabel(login_frame, text="Username").grid(row=0, column=0, pady=10, padx=10, sticky="w")
username_entry = ctk.CTkEntry(login_frame)
username_entry.grid(row=0, column=1, pady=10, padx=10)

ctk.CTkLabel(login_frame, text="Password").grid(row=1, column=0, pady=10, padx=10, sticky="w")
password_entry = ctk.CTkEntry(login_frame, show="*")
password_entry.grid(row=1, column=1, pady=10, padx=10)

ctk.CTkButton(login_frame, text="Register", command=register).grid(row=2, column=0, pady=10, padx=10)
ctk.CTkButton(login_frame, text="Login", command=login).grid(row=2, column=1, pady=10, padx=10)

# Cài đặt giao diện chat
chat_frame = ctk.CTkFrame(app)

ctk.CTkLabel(chat_frame, text="Receiver").grid(row=0, column=0, pady=10, padx=10, sticky="w")
receiver_entry = ctk.CTkEntry(chat_frame)
receiver_entry.grid(row=0, column=1, pady=10, padx=10)

ctk.CTkLabel(chat_frame, text="Message").grid(row=1, column=0, pady=10, padx=10, sticky="w")
message_entry = ctk.CTkEntry(chat_frame)
message_entry.grid(row=1, column=1, pady=10, padx=10)

ctk.CTkButton(chat_frame, text="Send Message", command=send_message).grid(row=2, column=0, columnspan=2, pady=10, padx=10)

# Cài đặt giao diện yêu cầu kết bạn
friend_request_frame = ctk.CTkFrame(app)
friend_request_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)

ctk.CTkLabel(friend_request_frame, text="Send Friend Request").grid(row=0, column=0, pady=10, padx=10, sticky="w")
friend_request_entry = ctk.CTkEntry(friend_request_frame)
friend_request_entry.grid(row=0, column=1, pady=10, padx=10)

ctk.CTkButton(friend_request_frame, text="Send Friend Request", command=send_friend_request).grid(row=1, column=0, columnspan=2, pady=10, padx=10)

# Cài đặt giao diện chấp nhận yêu cầu kết bạn
accept_friend_frame = ctk.CTkFrame(app)
accept_friend_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)

ctk.CTkLabel(accept_friend_frame, text="Accept Friend").grid(row=0, column=0, pady=10, padx=10, sticky="w")
accept_friend_entry = ctk.CTkEntry(accept_friend_frame)
accept_friend_entry.grid(row=0, column=1, pady=10, padx=10)

ctk.CTkButton(accept_friend_frame, text="Accept Friend", command=accept_friend_request).grid(row=1, column=0, columnspan=2, pady=10, padx=10)

# Cài đặt giao diện block người dùng
block_user_frame = ctk.CTkFrame(app)
block_user_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)

ctk.CTkLabel(block_user_frame, text="Block User").grid(row=0, column=0, pady=10, padx=10, sticky="w")
block_user_entry = ctk.CTkEntry(block_user_frame)
block_user_entry.grid(row=0, column=1, pady=10, padx=10)

ctk.CTkButton(block_user_frame, text="Block User", command=block_user).grid(row=1, column=0, columnspan=2, pady=10, padx=10)

# Kết nối tới server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("192.168.1.11", 7272))

app.mainloop()
