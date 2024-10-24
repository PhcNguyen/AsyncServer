# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import sys

from sources.manager.sql import MySQL, SQLite
from sources.server.tcpserver import TcpServer



if __name__ == "__main__":
    sql = MySQL() if "--mysql" in sys.argv else SQLite()
    tcp_server = TcpServer(TcpServer.LOCAL, TcpServer.PORT, sql)

    # Check for the '--nogui' argument
    if "--nogui" in sys.argv:
        from sources.ui.terminal import Terminal

        app = Terminal(tcp_server)
        Terminal.mainloop(app)
    else:
        from sources.ui.graphics import Graphics

        # Initialize Graphics only if --nogui is not present
        app = Graphics(Graphics.root, tcp_server)
        Graphics.root.mainloop()