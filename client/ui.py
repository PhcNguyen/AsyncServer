import socket
import threading
import json
from PyQt6.QtWidgets import (QApplication, QWidget,
                             QVBoxLayout, QLabel,
                             QLineEdit, QPushButton,
                             QTextEdit, QTabWidget)
from PyQt6.QtCore import pyqtSignal, QObject

class SocketManager(QObject):
    """Class to handle socket operations using blocking sockets."""
    data_received = pyqtSignal(str)  # Define a signal to emit when data is received

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.sock = None
        self.connected = False
        self.receive_thread = None

        # Connect the data_received signal to the update_log method of the app
        self.data_received.connect(self.app.update_log)

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
            self.receive_thread = threading.Thread(target=self.receive_data, daemon=True)
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
                self.sock.sendall(data.encode('utf-8'))
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
                    # Emit the data_received signal with the received data
                    self.data_received.emit(data.encode())
                else:
                    self.app.update_log("Connection closed by server.")
                    self.disconnect()
                    break
        except Exception as e:
            self.app.update_log(f"Error receiving data: {e}")
        finally:
            print("Receive thread has exited.")  # Log when thread ends


class ClientApp(QWidget):
    """UI class that handles user interface and interaction with SocketManager."""
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Client Application")
        self.setGeometry(100, 100, 600, 500)

        # Tab Widget
        self.tab_widget = QTabWidget(self)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.tab_widget)

        # Create tabs
        self.tab_connect = QWidget()
        self.tab_response = QWidget()
        self.tab_send_data = QWidget()

        self.tab_widget.addTab(self.tab_connect, "Kết nối")
        self.tab_widget.addTab(self.tab_response, "Nhận dữ liệu")
        self.tab_widget.addTab(self.tab_send_data, "Gửi Dữ Liệu")

        # Variables to hold socket and connection state
        self.socket_manager = SocketManager(self)

        # Declare UI components
        self.label_ip = None
        self.entry_ip = None
        self.label_port = None
        self.entry_port = None
        self.connection_status_label = None  # For the connection status inside the "Kết nối" tab

        # Create tabs
        self.create_connection_tab()
        self.create_response_tab()
        self.create_send_data_tab()

    def create_connection_tab(self):
        """Create the UI for the 'Kết nối' tab."""
        layout = QVBoxLayout()

        self.label_ip = QLabel("Địa chỉ IP:")
        self.entry_ip = QLineEdit()
        self.entry_ip.setText("192.168.1.2")  # Default IP

        self.label_port = QLabel("Cổng:")
        self.entry_port = QLineEdit()
        self.entry_port.setText("7272")  # Default Port

        # Connection status label
        self.connection_status_label = QLabel("Trạng thái kết nối: Ngắt kết nối")

        self.button_connect = QPushButton("Kết nối")
        self.button_disconnect = QPushButton("Ngắt kết nối")

        # Connect button signals
        self.button_connect.clicked.connect(self.connect_to_server)
        self.button_disconnect.clicked.connect(self.disconnect_from_server)

        # Add widgets to layout
        layout.addWidget(self.label_ip)
        layout.addWidget(self.entry_ip)
        layout.addWidget(self.label_port)
        layout.addWidget(self.entry_port)
        layout.addWidget(self.connection_status_label)
        layout.addWidget(self.button_connect)
        layout.addWidget(self.button_disconnect)

        self.tab_connect.setLayout(layout)

    def create_response_tab(self):
        """Create the UI for the 'Nhận dữ liệu' tab."""
        layout = QVBoxLayout()
        self.textbox = QTextEdit()
        self.textbox.setReadOnly(True)
        layout.addWidget(self.textbox)
        self.tab_response.setLayout(layout)

    def create_send_data_tab(self):
        """Create the UI for the 'Gửi Dữ Liệu' tab."""
        layout = QVBoxLayout()

        self.send_data_label = QLabel("Gửi:")
        self.send_entry = QLineEdit()

        self.send_button = QPushButton("Gửi")
        self.send_button.clicked.connect(self.send_data)

        layout.addWidget(self.send_data_label)
        layout.addWidget(self.send_entry)
        layout.addWidget(self.send_button)

        self.tab_send_data.setLayout(layout)

    def connect_to_server(self):
        """Handle the event when the user presses the Connect button."""
        ip = self.entry_ip.text()
        port = int(self.entry_port.text())
        self.socket_manager.connect(ip, port)

    def disconnect_from_server(self):
        """Handle the event when the user presses the Disconnect button."""
        self.socket_manager.disconnect()

    def send_data(self):
        """Handle the event when the user presses the Send Data button."""
        data = self.send_entry.text()
        self.socket_manager.send_data(data)  # Send formatted JSON
        self.update_log(f"Sent: \n{data}")

    def update_log(self, message):
        """Update the log area with new messages."""
        self.textbox.append(message)

    def update_connect_button(self, state):
        """Enable/disable the connect button."""
        self.button_connect.setEnabled(state)

    def update_send_button(self, state):
        """Enable/disable the send button."""
        self.send_button.setEnabled(state)

    def update_connection_status(self, status):
        """Update the connection status on the connection tab."""
        self.connection_status_label.setText(f"Trạng thái kết nối: {status}")

if __name__ == "__main__":
    app = QApplication([])

    client_app = ClientApp()
    client_app.show()

    app.exec()