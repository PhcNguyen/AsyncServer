# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

from sources.manager.database import DatabaseManager
from sources.application.ui.graphics import Graphics
from sources.application.server.tcpserver import TcpServer



# Initialize DatabaseManager, Graphics, TcpServer
tcp_server = TcpServer(TcpServer.LOCAL,TcpServer.PORT, DatabaseManager())
app = Graphics(Graphics.root, tcp_server)


if __name__ == "__main__":
    # Khởi động chương trình
    Graphics.root.mainloop()