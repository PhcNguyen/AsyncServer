# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

from src.server.graphics import Graphics
from src.manager.mysqlite import DBManager
from src.server.networks import AsyncNetworks, Networks
from src.manager.algorithm import AlgorithmHandler


"""
| Feature                      | V1                              | V2                                             |
|------------------------------|---------------------------------|------------------------------------------------|
| **Network Type**             | Synchronous (`Networks`)        | Asynchronous (`AsyncNetworks`)                 |
| **Responsiveness**           | Potentially blocked GUI         | Responsive GUI                                 |
| **Complexity**               | Simpler network management      | More complex, requires handling of async calls |
| **Use Case Suitability**     | Basic use cases, low concurrency| High concurrency, real-time applications       |

"""


# Initialize DatabaseManager, Networks, and Graphics: V1
def v1():
    sql = DBManager(DBManager.db_path)
    networks = Networks(AsyncNetworks.host, AsyncNetworks.port, AlgorithmHandler(sql))
    app = Graphics(Graphics.root, networks)
    Graphics.root.mainloop()


# Initialize DatabaseManager, AsyncNetworks, and Graphics: V2
def v2():
    sql = DBManager(DBManager.db_path)
    async_networks = AsyncNetworks(AsyncNetworks.host, AsyncNetworks.port, AlgorithmHandler(sql))
    app = Graphics(Graphics.root, async_networks)
    Graphics.root.mainloop()



if __name__ == "__main__":
    # Khởi động Tkinter
    v2()