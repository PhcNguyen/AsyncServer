
# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

from src.server.graphics import Graphics
from src.server.networks import Networks
from src.server.algorithm import Algorithm
from src.server.mysqlite import DatabaseManager


sql = DatabaseManager(DatabaseManager.db_path)
networks = Networks(Networks.host, Networks.port, Algorithm(sql))

app = Graphics(Graphics.root, networks)


Graphics.root.mainloop()