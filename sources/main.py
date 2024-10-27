# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import sys

from sources.manager.sql import MySQL, SQLite
from sources.server.tcpserver import TCPServer



if __name__ == "__main__":
    sql = MySQL() if "--mysql" in sys.argv else SQLite()
    tcp_server = TCPServer(TCPServer.LOCAL, TCPServer.PORT, sql)

    # Check for the '--nogui' argument
    if "--nogui" in sys.argv:
        from sources.ui.terminal import Terminal

        app = Terminal(tcp_server)
        Terminal.mainloop(app)
    else:
        from sources.ui.graphics import Graphics

        # Initialize Graphics only if --nogui is not present
        app = Graphics(Graphics.root)
        app.setup_server(tcp_server)

        Graphics.root.mainloop()