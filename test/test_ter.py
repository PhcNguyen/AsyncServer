import asyncio
import threading
from src.server.utils import System
from src.models.types import NetworksTypes
from src.server.utils import InternetProtocol
from src.manager.mysqlite import DBManager
from src.manager.algorithm import AlgorithmHandler
from src.server.networks import AsyncNetworks


class GraphicsTerminal:
    def __init__(self, server: NetworksTypes):
        self.server = None
        self.network = server

        self.current_log = None  # Biến để theo dõi log hiện tại

        # Khởi tạo vòng lặp sự kiện
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        # Tạo và chạy luồng cho vòng lặp sự kiện
        self.loop_thread = threading.Thread(target=self.loop.run_forever, daemon=True)
        self.loop_thread.start()

    def start_server(self):
        if self.server:
            self._log_to_terminal("Server is already running.")
            return

        """Bắt đầu server với coroutine."""
        asyncio.run_coroutine_threadsafe(self._start_server(), self.loop)

    def stop_server(self):
        if not self.server:
            self._log_to_terminal("Server is not running.")
            return

        try:
            asyncio.run_coroutine_threadsafe(self._stop_server(), self.loop)
        except Exception as e:
            self._log_to_terminal(f"Error while trying to stop the server: {e}")

    def _log_to_terminal(self, message: str):
        """Ghi log ra terminal."""
        print(message)

    def log_message(self, message: str):
        """Nhận thông báo từ Networks và phân loại nó để hiển thị trên terminal."""
        if "Notify:" in message:
            self._log_to_terminal(f"Notify: {message.split('Notify:')[-1].strip()}")
        elif "Error:" in message:
            self._log_to_terminal(f"Error: {message.split('Error:')[-1].strip()}")
        else:
            self._log_to_terminal(f"Unknown message: {message}")

    async def _update_server_info(self):
        """Cập nhật thông tin server trong terminal."""
        if self.server:
            local_ip = InternetProtocol.local()
            public_ip = InternetProtocol.public()
            ping = f"{InternetProtocol.ping()} ms"
            print(f"Local IP: {local_ip}, Public IP: {public_ip}, Ping: {ping}")
        else:
            print("Server not running. IP and ping are not available.")

    
    async def _start_server(self):
        if self.server:
            self._log_to_terminal("Server is already running.")
            return
        try:
            self.network.set_message_callback(self.log_message)
            self.server = self.network

            await asyncio.gather(
                self.server.start(),  # Đảm bảo đây là coroutine
                self._update_server_info()
            )
        except Exception as e:
            self._log_to_terminal(f"Error starting server: {e}")
    
    async def _stop_server(self):
        if self.server:
            try:
                await self.server.stop()  # Chạy lệnh dừng server
                self._log_to_terminal("Server stopped successfully.")
            except Exception as e:
                self._log_to_terminal(f"Error while stopping the server: {e}")
            finally:
                self.server = None
                await self._update_server_info()  # Cập nhật thông tin sau khi dừng server

    def shutdown(self):
        """Dừng tất cả các tiến trình và vòng lặp trước khi thoát."""
        if self.server:
            self.stop_server()
        
        # Dừng vòng lặp asyncio
        self.loop.call_soon_threadsafe(self.loop.stop)

        # Đợi thread kết thúc
        self.loop_thread.join()
        print("Application has shut down.")


if __name__ == "__main__":
    sql = DBManager(DBManager.db_path)
    async_networks = AsyncNetworks(AsyncNetworks.host, AsyncNetworks.port, AlgorithmHandler(sql))
    app = GraphicsTerminal(async_networks)

    try:
        while True:
            command = input("Enter command (start/stop/exit): ").strip().lower()
            if command == "start":
                app.start_server()
            elif command == "stop":
                app.stop_server()
            elif command == "exit":
                print("Stopping the server before exiting...")
                app.stop_server()  # Ensure the server is stopped
                break  # Exit the loop
            else:
                print("Unknown command.")
    except KeyboardInterrupt:
        print("\nExiting...")  # Optional: print a message
        app.stop_server()  # Ensure server stops before exiting
        System.exit()
