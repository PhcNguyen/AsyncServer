# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import asyncio
import uuid

from sources import configs
from sources.manager.commands import Cmd
from sources.model.security.cipher import Cipher
from sources.model.logging.serverlogger import AsyncLogger


class ConnectionManager:
    def __init__(self, server, transport=None):
        self.server = server
        self.transport = transport
        self.is_connected = False

    async def connect(self):
        self.is_connected = True
        await AsyncLogger.notify(f"Connected session on {self.server}.")

    async def disconnect(self):
        if self.is_connected:
            self.is_connected = False
            await AsyncLogger.notify(f"Disconnected session from {self.server}.")
            if self.transport:
                self.transport.close()


class DataHandler:
    BUFFER_SIZE = 8192  # Chuyển thành hằng số lớp

    def __init__(self, transport=None):
        self.transport = transport
        self.bytes_sent = 0
        self.bytes_received = 0
        self.send_buffer = bytearray()

    async def send(self, data):
        self.send_buffer.extend(data)
        await self._try_send()

    async def _try_send(self):
        while self.send_buffer:
            try:
                sent = self.transport.send(self.send_buffer)
                self.bytes_sent += sent
                self.send_buffer = self.send_buffer[sent:]
                await AsyncLogger.notify(f"Sent {sent} bytes.")
            except Exception as e:
                await AsyncLogger.notify_error(f"Error during send: {e}")
                break

    async def receive(self):
        while True:
            try:
                data = await asyncio.wait_for(self.transport.recv(self.BUFFER_SIZE), timeout=1.0)
                if not data:
                    return None
                self.bytes_received += len(data)
                return data
            except asyncio.TimeoutError:
                continue  # Continue on timeout
            except Exception as e:
                await AsyncLogger.notify_error(f"Error during receive: {e}")
                break


class CommandHandler:
    def __init__(self, sqlite, cipher):
        self.sqlite = sqlite
        self.cipher = cipher

        # Ánh xạ các lệnh đến các phương thức xử lý tương ứng
        self.command_map = {
            Cmd.LOGIN: self.handle_login,
            Cmd.LOGOUT: self.handle_logout,
            Cmd.REGISTER: self.handle_register,
            Cmd.PLAYER_INFO: self.handle_player_info
        }

    async def handle_command(self, data):
        command = data.get("command")
        handler = self.command_map.get(command)
        if handler:
            return await handler(data)
        return {"error": f"Unknown command: {command}"}

    async def handle_login(self, data):
        username = data.get("username", "")
        password = data.get("password", "")
        if not username or not password:
            return {"error": "Username or password is missing"}
        await self.sqlite.login(username, password)

    @staticmethod
    async def handle_logout(data):
        return "Logout not implemented"

    async def handle_register(self, data):
        username = data.get("username", "")
        password = data.get("password", "")
        ip_address = data.get("ip_address", "")
        if not username or not password or not ip_address:
            return {"error": "Username, password or IP address is missing"}
        await self.sqlite.insert_account(username, password, ip_address)

    async def handle_player_info(self, data):
        username = data.get("username", "")
        if not username:
            return {"error": "Username is missing"}
        await self.sqlite.get_player_coin(username)


class TcpSession:
    CLIENT_COUNT = 0  # Thêm thuộc tính lớp để theo dõi số lượng client kết nối
    MAX_CONNECTIONS = 1000000  # Giới hạn số lượng kết nối tối đa

    def __init__(self, server, sql):
        self.sqlite = sql
        self.server = server
        self.is_connected = False  # Thêm thuộc tính này để theo dõi trạng thái kết nối
        self.id = uuid.uuid4()
        self.cipher = Cipher(
            configs.file_paths("public_key.pem"),
            configs.file_paths("private_key.pem")
        )
        self.connection_manager = ConnectionManager(server)
        self.data_handler = DataHandler()
        self.command_handler = CommandHandler(sql, self.cipher)

    async def receive_data(self):
        while self.is_connected:  # Thay vì kiểm tra connection_manager.is_connected
            data = await self.data_handler.receive()
            if data:
                decrypted_data = self.cipher.decrypt(data)
                if decrypted_data:
                    await self.command_handler.handle_command(decrypted_data)
                else:
                    await self.data_handler.send({
                        "status": False,
                        "message": "Decryption failed: No data returned.",
                        "key_server": self.cipher.public_key
                    })
            else:
                await self.disconnect()

    async def connect(self, reader, writer):
        if TcpSession.CLIENT_COUNT >= TcpSession.MAX_CONNECTIONS:
            # Nếu đã đạt giới hạn kết nối, đóng kết nối và thông báo cho client
            await writer.drain()  # Đảm bảo dữ liệu đã được gửi đi
            await writer.write(b"Server is busy. Please try again later.")
            writer.close()
            await AsyncLogger.notify(
                f"Connection attempt rejected. Max connections reached: {TcpSession.MAX_CONNECTIONS}")
            return

        self.connection_manager.transport = writer
        await self.connection_manager.connect()
        self.is_connected = True

        # Cập nhật số lượng client kết nối
        TcpSession.CLIENT_COUNT += 1
        await AsyncLogger.notify(f"Connected: {self.id}, Current client count: {TcpSession.MAX_CONNECTIONS}")

        asyncio.create_task(self.receive_data())

    async def disconnect(self):
        self.is_connected = False
        await self.connection_manager.disconnect()

        # Giảm số lượng client kết nối khi ngắt kết nối
        TcpSession.CLIENT_COUNT -= 1
        await AsyncLogger.notify(f"Disconnected: {self.id}, Current client count: {TcpSession.CLIENT_COUNT}")

    async def close(self):
        await self.sqlite.close()
