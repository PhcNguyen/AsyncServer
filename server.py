
# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

from models.graphics import Graphics
from models.networks import Networks



networks = Networks(Networks.host, Networks.port)
app = Graphics(Graphics.root, networks)

Graphics.root.mainloop()