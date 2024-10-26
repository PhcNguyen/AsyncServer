import sys
from client.ui import QApplication, LoginWindow
from client.network import SocketManager


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Initialize the socket manager and connect to the server
    socket_manager = SocketManager(host="192.168.1.2", port=7272)
    socket_manager.connect()

    # Start the login window
    login_window = LoginWindow(socket_manager)
    login_window.show()

    # Close the socket when the application exits
    app.aboutToQuit.connect(socket_manager.close)

    sys.exit(app.exec())
