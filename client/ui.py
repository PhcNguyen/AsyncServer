
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox)
from PyQt6.QtCore import pyqtSignal, pyqtSlot, QObject




class LoginWindow(QWidget):
    def __init__(self, socket_manager):
        super().__init__()

        self.socket_manager = socket_manager
        self.setWindowTitle("Login")
        self.resize(300, 150)

        # Create widgets
        self.email_label = QLabel('Email:', self)
        self.email_input = QLineEdit(self)

        self.password_label = QLabel('Password:', self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.login_button = QPushButton('Login', self)
        self.register_button = QPushButton('Register', self)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)

        self.setLayout(layout)

        # Connect buttons to functions
        self.login_button.clicked.connect(self.login)
        self.register_button.clicked.connect(self.register)


    def login(self):
        """Send login request to the server."""
        email = self.email_input.text()
        password = self.password_input.text()

        if not email or not password:
            QMessageBox.warning(self, "Input Error", "Please enter both email and password.")
            return

        request = {
            "command": 0,
            "email": email,
            "password": password
        }

        response = self.socket_manager.send_request(request)

        if response.get("status") == "success":
            QMessageBox.information(self, "Success", "Logged in successfully!")
        else:
            QMessageBox.warning(self, "Login Failed", response.get("message", "Unknown error."))

    def register(self):
        """Open the registration form."""
        self.registration_window = RegistrationWindow(self.socket_manager)
        self.registration_window.show()


class RegistrationWindow(QWidget):
    def __init__(self, socket_manager):
        super().__init__()

        self.socket_manager = socket_manager
        self.init_ui()

    def init_ui(self):
        """Initialize the registration UI."""
        self.setWindowTitle("Register")
        self.resize(300, 150)

        # Create widgets
        self.email_label = QLabel('Email:', self)
        self.email_input = QLineEdit(self)

        self.password_label = QLabel('Password:', self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.register_button = QPushButton('Register', self)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.register_button)

        self.setLayout(layout)

        # Connect button to function
        self.register_button.clicked.connect(self.register)

    def register(self):
        """Send registration request to the server."""
        email = self.email_input.text()
        password = self.password_input.text()

        if not email or not password:
            QMessageBox.warning(self, "Input Error", "Please enter both email and password.")
            return

        request = {
            "command": 2,
            "email": email,
            "password": password
        }

        response = self.socket_manager.send_request(request)
        print(response)

        if response.get("status"):
            QMessageBox.information(self, "Success", "Registered successfully!")
            self.close()
        else:
            QMessageBox.warning(self, "Registration Failed", response.get("message", "Unknown error."))
