# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import os
import time
import typing
import asyncio
import aiofiles

from sources import configs
from collections import OrderedDict
from sources.manager.files import iofiles



class FileCache:
    def __init__(self):
        # Khởi tạo bộ nhớ cache sử dụng OrderedDict
        self._cache = OrderedDict()
        self._timeouts = {}  # Thời gian timeout cho mỗi file
        self._file_mtimes = {}  # Thời gian sửa đổi cuối cùng của các file
        self.file_path = configs.file_paths("log.cache")  # Đường dẫn đến file cache
        self.lock = asyncio.Lock()  # Khóa bất đồng bộ cho an toàn khi truy cập

    def add(self, key, value, timeout=0):
        """Thêm một file vào bộ nhớ cache với thời gian timeout tùy chọn."""
        if key in self._cache:
            del self._cache[key]  # Xóa key cũ nếu tồn tại
        self._cache[key] = value  # Thêm key mới vào cache
        if timeout > 0:
            self._timeouts[key] = time.time() + timeout  # Đặt thời gian timeout

    def find(self, key):
        """Tìm một file trong bộ nhớ cache."""
        if key in self._cache:
            if key in self._timeouts and time.time() > self._timeouts[key]:
                del self._cache[key]  # Xóa file nếu quá thời gian timeout
                del self._timeouts[key]
                return False, None
            return True, self._cache[key]  # Trả về file nếu tìm thấy
        return False, None  # Không tìm thấy

    def remove(self, key):
        """Xóa một file khỏi bộ nhớ cache."""
        if key in self._cache:
            del self._cache[key]  # Xóa key từ cache
            if key in self._timeouts:
                del self._timeouts[key]
            if key in self._file_mtimes:
                del self._file_mtimes[key]
            return True  # Trả về True nếu xóa thành công
        return False  # Không tìm thấy key để xóa

    def clear(self):
        """Xóa tất cả các mục trong bộ nhớ cache."""
        self._cache.clear()  # Xóa cache
        self._timeouts.clear()  # Xóa thời gian timeout
        self._file_mtimes.clear()  # Xóa thời gian sửa đổi file

    async def watch_files(self, path, interval=1):
        """Bắt đầu kiểm tra định kỳ các thay đổi file một cách bất đồng bộ."""
        while True:
            await asyncio.sleep(interval)  # Chờ trong một khoảng thời gian
            await self.check_files(path)  # Kiểm tra thay đổi file

    async def check_files(self, path):
        """Kiểm tra các thay đổi trong thư mục hoặc các file."""
        for root, _, files in os.walk(path):  # Duyệt qua thư mục
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    mtime = os.path.getmtime(file_path)  # Lấy thời gian sửa đổi
                    if file_path not in self._file_mtimes:
                        # File mới được tìm thấy, thêm vào cache
                        self._file_mtimes[file_path] = mtime
                        with open(file_path, 'rb') as f:
                            content = f.read()
                        self.add(file_path, content)  # Thêm vào cache
                        print(f"File added to cache: {file_path}")  # Thông báo đã thêm file
                    elif mtime > self._file_mtimes[file_path]:
                        # File đã thay đổi, cập nhật cache
                        self._file_mtimes[file_path] = mtime
                        with open(file_path, 'rb') as f:
                            content = f.read()
                        self.add(file_path, content)  # Cập nhật cache
                        print(f"File updated in cache: {file_path}")  # Thông báo đã cập nhật file
                except FileNotFoundError:
                    pass  # Bỏ qua nếu file không tồn tại

    def start(self, path, interval=1):
        """Bắt đầu theo dõi thư mục."""
        loop = asyncio.get_event_loop()  # Lấy vòng lặp sự kiện
        loop.run_until_complete(self.watch_files(path, interval))  # Chạy hàm theo dõi

    async def read_lines(self, file_path: None | str = None) -> typing.List[str]:
        """Đọc tất cả các dòng từ file và trả về dưới dạng danh sách."""
        if file_path:
            path = configs.file_paths(file_path)
        else:
            path = self.file_path
        async with self.lock:  # Đảm bảo truy cập an toàn
            if not os.path.exists(path):
                return []  # Trả về danh sách rỗng nếu file không tồn tại

            async with aiofiles.open(path, 'r+', encoding='utf-8') as file:
                lines = await file.readlines()  # Đọc tất cả các dòng
                if not lines:
                    return []  # Trả về danh sách rỗng nếu không có dòng nào

                # Xóa các ký tự trắng ở đầu/cuối mỗi dòng
                lines = [line.strip() for line in lines]

                # Xóa nội dung file sau khi đọc
                await file.seek(0)  # Đặt con trỏ về đầu file
                await file.writelines(lines[0:0])  # Ghi lại bằng các dòng rỗng
                await file.truncate()  # Cắt bỏ phần còn lại của nội dung

            return lines  # Trả về danh sách các dòng đã đọc

    async def write(self, string: str, file_path: None | str = None) -> None:
        """Ghi một dòng vào file."""
        if file_path:
            path = configs.file_paths(file_path)
        else:
            path = self.file_path
        async with self.lock:  # Đảm bảo truy cập an toàn
            # Thêm dòng mới vào file
            await iofiles.write_files(path, (string + '\n'), mode='a')

    async def clear_file(self, file_path: None | str = None) -> None:
        """Xóa toàn bộ nội dung từ file cache."""
        if file_path:
            path = configs.file_paths(file_path)
        else:
            path = self.file_path
        async with self.lock:  # Đảm bảo truy cập an toàn
             # Ghi một chuỗi rỗng để xóa nội dung
             await iofiles.write_files(path, content="", mode='a')
