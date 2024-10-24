# Bản quyền (C) của PhcNguyen Developers
# Phân phối theo các điều khoản của Giấy phép BSD đã sửa đổi.

import asyncio



class AccountManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager
    async def info(self, email: str) -> dict: ...
    async def lock(self, user_id: int) -> dict: ...
    async def logout(self, user_id: int) -> dict: ...
    async def delete(self, user_id: int) -> dict: ...
    async def login(self, email: str, password: str) -> dict: ...
    async def register(self, email: str, password: str) -> dict: ...
    async def change_password(self, user_id: int, old_password: str, new_password: str) -> dict: ...
    async def update_last_login(self, email): ...


class PlayerManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager
    async def dump_data(self, **kwargs) -> bool: ...
    async def get(self, user_id: int) -> dict: ...
    async def update(self, user_id: int, **kwargs) -> dict: ...


class TableManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager
    async def create_tables(self) -> bool: ...


class SQLite:
    """
    Lớp DBManager dùng để quản lý các thao tác với cơ sở dữ liệu.

    Thuộc tính:
    - db_path: Đường dẫn tới tệp cơ sở dữ liệu.

    Phương thức:
    - insert_account: Thêm tài khoản mới vào cơ sở dữ liệu.
    - login: Xác thực thông tin đăng nhập của người dùng.
    - get_player_coin: Lấy số dư coin của một người chơi cụ thể.
    """

    def __init__(self) -> None:
        self.conn = None
        self.lock = asyncio.Lock()
        self.config = None
        self.type = None
        self.table: TableManager = TableManager(None)
        self.player: PlayerManager = PlayerManager(None)
        self.account: AccountManager = AccountManager(None)

    async def start(self) -> bool: ...
    async def close(self) -> bool: ...

class MySQL:
    """
    Lớp DBManager dùng để quản lý các thao tác với cơ sở dữ liệu.

    Thuộc tính:
    - db_path: Đường dẫn tới tệp cơ sở dữ liệu.

    Phương thức:
    - insert_account: Thêm tài khoản mới vào cơ sở dữ liệu.
    - login: Xác thực thông tin đăng nhập của người dùng.
    - get_player_coin: Lấy số dư coin của một người chơi cụ thể.
    """

    def __init__(self) -> None:
        self.conn = None
        self.lock = asyncio.Lock()
        self.config = None
        self.type = None
        self.table: TableManager = TableManager(None)
        self.player: PlayerManager = PlayerManager(None)
        self.account: AccountManager = AccountManager(None)

    async def start(self) -> bool: ...
    async def close(self) -> bool: ...


class TcpSession:
    """
    Lớp TcpSession để quản lý kết nối TCP cho mỗi phiên làm việc.

    Phương thức:
    - connect: Thiết lập kết nối TCP giữa client và server.
    - receive_data: Nhận dữ liệu từ client.
    - disconnect: Ngắt kết nối từ client.
    - close: Đóng phiên làm việc.
    """
    def __init__(self, server, database: SQLite | MySQL): ...
    async def connect(self, reader, writer): ...
    async def receive_data(self): ...
    async def disconnect(self): ...
    async def close(self): ...


class ClientHandler:
    """
    Lớp ClientHandler quản lý và xử lý các kết nối client.

    Phương thức:
    - handle_client: Xử lý kết nối từ một client cụ thể.
    - close_connection: Đóng kết nối với một phiên client.
    - close_all_connections: Đóng tất cả các kết nối hiện có.
    """
    def __init__(self, database: SQLite | MySQL): ...
    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter): ...
    async def close_connection(self, session: TcpSession): ...
    async def close_all_connections(self): ...


class TcpServer:
    PORT: int = ...
    LOCAL: str = ...
    PUBLIC: str = ...

    def __init__(self, host: str, port: int, database: SQLite | MySQL):
        """Khởi tạo cài đặt mạng và hàm xử lý dữ liệu."""
        self.host = host
        self.port = port
        self.running: bool = False

        self.stop_event = asyncio.Event()
        self.server_address: [str, int] = (host, port)
        self.running: bool = False
        self.client_handler = ...
        self.current_connections = 0  # Số lượng kết nối hiện tại

    async def start(self): ...
    async def stop(self): ...