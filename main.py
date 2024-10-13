# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

from src.server.utils import System
from src.manager.mysqlite import DBManager
from src.manager.algorithm import AlgorithmHandler
from src.server.graphics import Graphics, Graphics2
from src.server.networks import Networks, AsyncNetworks
 

# Initialize DatabaseManager, Graphics2, AsyncNetworks
sql = DBManager(DBManager.db_path)
async_networks = AsyncNetworks(AsyncNetworks.host, AsyncNetworks.port, AlgorithmHandler(sql))  
app = Graphics2(Graphics2.root, async_networks)


if __name__ == "__main__":
    # Khởi động chương trình
    Graphics2.root.mainloop()