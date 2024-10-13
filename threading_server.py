
# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import threading

from src.server.graphics import Graphics
from src.server.networks import Networks
from src.server.mysqlite import DBManager
from src.server.algorithm import AlgorithmHandler



# Initialize DatabaseManager, Networks, and Graphics
sql = DBManager(DBManager.db_path)
networks = Networks(Networks.host, Networks.port, AlgorithmHandler(sql))
app = Graphics(Graphics.root, networks)

# Start the networking server in a separate thread
def start_networks():
    networks.start()  # Assuming networks has a start method to run the server

network_thread = threading.Thread(target=start_networks)
network_thread.daemon = True
network_thread.start()

# Handle shutdown gracefully
def on_close():
    networks.stop()  # Stop server
    sql.close()  # Close database
    Graphics.root.destroy()  # Close GUI

Graphics.root.protocol("WM_DELETE_WINDOW", on_close)
Graphics.root.mainloop()