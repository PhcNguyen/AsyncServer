import customtkinter as ctk
import socket
import threading

class SocketManager:
    """Class to handle socket operations using blocking sockets."""
    def __init__(self, app):
        self.app = app
        self.sock = None
        self.connected = False
        self.receive_thread = None

    def connect(self, ip, port):
        """Connect to the server using a blocking socket."""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((ip, port))
            self.connected = True
            self.app.update_log(f"Connected to {ip}:{port}")

            # Enable the "Send Data" button and disable "Connect" button
            self.app.update_connect_button(False)
            self.app.update_send_button(True)

            # Update connection status tab
            self.app.update_connection_status("Connected")

            # Start a new thread to receive data
            self.receive_thread = threading.Thread(target=self.receive_data)
            self.receive_thread.start()

        except Exception as e:
            self.app.update_log(f"Error connecting to server: {e}")
            self.app.update_connection_status("Failed to Connect")

    def disconnect(self):
        """Disconnect from the server."""
        if self.connected:
            try:
                self.sock.close()
                self.connected = False
                self.app.update_log("Disconnected from server.")

                # Stop receiving data by joining the thread
                if self.receive_thread:
                    self.receive_thread.join()

                self.app.update_connect_button(True)
                self.app.update_send_button(False)

                # Update connection status tab
                self.app.update_connection_status("Disconnected")

            except Exception as e:
                self.app.update_log(f"Error during disconnect: {e}")
        else:
            self.app.update_log("Not connected to any server.")

    def send_data(self, data):
        """Send data to the server."""
        if self.connected:
            try:
                self.sock.sendall(data.encode())
                self.app.update_log(f"Sent: {data}")
            except Exception as e:
                self.app.update_log(f"Error sending data: {e}")
        else:
            self.app.update_log("Not connected to any server.")

    def receive_data(self):
        """Receive data from the server."""
        try:
            while self.connected:
                data = self.sock.recv(1024)
                if data:
                    self.app.update_log(f"Server: {data.decode()}")
                else:
                    self.app.update_log("Connection closed by server.")
                    self.disconnect()
                    break
        except Exception as e:
            self.app.update_log(f"Error receiving data: {e}")

class ClientApp(ctk.CTk):
    """UI class that handles user interface and interaction with SocketManager."""
    def __init__(self):
        super().__init__()

        self.send_button = None
        self.send_entry = None
        self.send_data_label = None
        self.title("Client Application")
        self.geometry("600x500")

        # TabView
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(expand=True, fill="both")

        # Tạo các tab: "Kết nối", "Nhận dữ liệu", "Send Data"
        self.tab_connect = self.tab_view.add("Kết nối")
        self.tab_response = self.tab_view.add("Nhận dữ liệu")
        self.tab_send_data = self.tab_view.add("Send Data")  # Tab mới để gửi dữ liệu

        # Variables to hold socket and connection state
        self.socket_manager = SocketManager(self)

        # Declare UI components as instance attributes
        self.label_ip = None
        self.entry_ip = None
        self.label_port = None
        self.entry_port = None
        self.label_data = None
        self.entry_data = None
        self.button_connect = None
        self.button_disconnect = None
        self.button_send = None
        self.textbox = None
        self.connection_status_label = None  # For the connection status inside the "Kết nối" tab

        # Create the connection tab first to initialize UI elements
        self.create_connection_tab()

        # Create the response tab
        self.create_response_tab()

        # Create the send data tab
        self.create_send_data_tab()

    def create_connection_tab(self):
        """Tạo giao diện cho tab 'Kết nối'"""
        self.label_ip = ctk.CTkLabel(self.tab_connect, text="IP Address:")
        self.label_ip.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.entry_ip = ctk.CTkEntry(self.tab_connect)
        self.entry_ip.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.entry_ip.insert(0, "192.168.1.2")  # Default IP

        self.label_port = ctk.CTkLabel(self.tab_connect, text="Port:")
        self.label_port.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.entry_port = ctk.CTkEntry(self.tab_connect)
        self.entry_port.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        self.entry_port.insert(0, "7272")  # Default Port

        # Update connection status label
        self.connection_status_label = ctk.CTkLabel(self.tab_connect, text="Connection Status: Disconnected", font=("Arial", 12))
        self.connection_status_label.grid(row=2, column=0, columnspan=2, pady=10)

        self.button_connect = ctk.CTkButton(self.tab_connect, text="Connect", command=self.connect_to_server)
        self.button_connect.grid(row=3, column=0, padx=10, pady=10, sticky="w")

        self.button_disconnect = ctk.CTkButton(self.tab_connect, text="Disconnect", command=self.disconnect_from_server)
        self.button_disconnect.grid(row=3, column=1, padx=10, pady=10, sticky="w")

    def create_response_tab(self):
        """Tạo giao diện cho tab 'Nhận dữ liệu'"""
        self.textbox = ctk.CTkTextbox(self.tab_response, height=20, width=70)
        self.textbox.pack(pady=10, padx=10, expand=True, fill="both")

    def create_send_data_tab(self):
        """Tạo giao diện cho tab 'Send Data'"""
        self.send_data_label = ctk.CTkLabel(self.tab_send_data, text="Data to send:", font=("Arial", 14))
        self.send_data_label.pack(pady=10, padx=10)

        self.send_entry = ctk.CTkEntry(self.tab_send_data, width=400)  # Make it wider
        self.send_entry.pack(pady=10, padx=10)

        self.send_button = ctk.CTkButton(self.tab_send_data, text="Send", command=self.send_data)
        self.send_button.pack(pady=10)

    def connect_to_server(self):
        """Xử lý khi người dùng nhấn nút Connect"""
        ip = self.entry_ip.get()
        port = int(self.entry_port.get())
        self.socket_manager.connect(ip, port)

    def disconnect_from_server(self):
        """Xử lý khi người dùng nhấn nút Disconnect"""
        self.socket_manager.disconnect()

    def send_data(self):
        """Xử lý khi người dùng nhấn nút Send Data"""
        data = self.send_entry.get()  # Get data from send tab
        self.socket_manager.send_data(data)

    def update_log(self, message):
        """Update the log area with new messages"""
        self.textbox.insert("end", f"{message}\n")
        self.textbox.yview("end")

    def update_connect_button(self, state):
        """Enable/disable the connect button"""
        self.button_connect.configure(state="normal" if state else "disabled")

    def update_send_button(self, state):
        """Enable/disable the send button"""
        self.button_send.configure(state="normal" if state else "disabled")

    def update_connection_status(self, status):
        """Update the connection status on the connection tab"""
        if self.connection_status_label:  # Ensure the label exists
            self.connection_status_label.configure(text=f"Connection Status: {status}")


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")  # Optional: change to 'light' if needed
    ctk.set_default_color_theme("blue")

    # Run the application
    app = ClientApp()

    # Start the event loop for the application
    app.mainloop()
