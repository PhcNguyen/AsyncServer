# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

from test.client.graphics import AuthMenu


if __name__ == "__main__":
    app = AuthMenu(AuthMenu.root)
    AuthMenu.root.mainloop()