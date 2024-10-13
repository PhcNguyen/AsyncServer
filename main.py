# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

from src.server.graphics import Graphics
from src.manager.mysqlite import DBManager
from src.server.networks import AsyncNetworks
from src.manager.algorithm import AlgorithmHandler



# Initialize DatabaseManager, AsyncNetworks, and Graphics
sql = DBManager(DBManager.db_path)
async_networks = AsyncNetworks(AsyncNetworks.host, AsyncNetworks.port, AlgorithmHandler(sql))
app = Graphics(Graphics.root, async_networks)


if __name__ == "__main__":
    # Khởi động Tkinter
    Graphics.root.mainloop()