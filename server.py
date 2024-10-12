
# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

from models.graphics import Graphics
from models.networks import Networks
from models.mysqlite import DatabaseManager
from models.algorithm import Algorithm



sql = DatabaseManager(DatabaseManager.db_path)
networks = Networks(Networks.host, Networks.port, Algorithm(sql))

app = Graphics(Graphics.root, networks)


Graphics.root.mainloop()