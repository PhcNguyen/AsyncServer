# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import sys
from sources.manager.sql import DatabaseManager
from sources.server.tcpserver import TcpServer

# Initialize DatabaseManager and TcpServer
sqlite = DatabaseManager()
tcp_server = TcpServer(TcpServer.LOCAL, TcpServer.PORT, sqlite)


if __name__ == "__main__":
    # Check for the '--nogui' argument
    if "--nogui" in sys.argv:
        from sources.ui import terminal

        app = terminal.Terminal(tcp_server)

        terminal.mainloop(app)
    else:
        from sources.ui.graphics import Graphics

        # Initialize Graphics only if --nogui is not present
        app = Graphics(Graphics.root, tcp_server, None)
        # Start the GUI main loop
        Graphics.root.mainloop()