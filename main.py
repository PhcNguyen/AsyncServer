# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

from sources.manager.database import DatabaseManager
from sources.application.graphics import Graphics
from sources.application.networks import AsyncNetworks
from sources.manager.handlers import AlgorithmProcessing



# Initialize DatabaseManager, Graphics, AsyncNetworks
async_networks = AsyncNetworks(
    AsyncNetworks.local, 
    AsyncNetworks.port, 
    AlgorithmProcessing(DatabaseManager())
)  
app = Graphics(Graphics.root, async_networks)


if __name__ == "__main__":
    # Khởi động chương trình
    Graphics.root.mainloop()