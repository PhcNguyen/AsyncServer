# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import os
import time
import typing
import asyncio
import aiofiles

from sources import configs
from collections import OrderedDict



class FileCache:
    """A class for caching files with support for file watching and timeouts."""

    def __init__(self):
        self._cache = OrderedDict()  # Store cached files in an ordered dictionary
        self._timeouts = {}  # Store expiration times for cache entries
        self._file_mtimes = {}  # Store last modified times for watched files
        self.file_path = configs.file_paths("log.cache")  # Path to the default cache file
        self.lock = asyncio.Lock()  # Async lock for thread-safe access

    def add(self, key: str, value: typing.Any, timeout: int = 0):
        """Add an item to the cache with an optional timeout."""
        self._cache[key] = value  # Add or update the cache entry
        if timeout > 0:
            self._timeouts[key] = time.time() + timeout  # Set expiration time

    def find(self, key: str) -> typing.Tuple[bool, typing.Any]:
        """Find a file in the cache and return a tuple (found: bool, value)."""
        if key in self._cache:
            if key in self._timeouts and time.time() > self._timeouts[key]:
                self.remove(key)  # Remove expired entry
                return False, None
            return True, self._cache[key]
        return False, None

    def remove(self, key: str) -> bool:
        """Remove an item from the cache."""
        if key in self._cache:
            del self._cache[key]
            self._timeouts.pop(key, None)  # Remove timeout if present
            self._file_mtimes.pop(key, None)  # Remove file modification time if present
            return True
        return False

    def clear(self):
        """Clear the entire cache."""
        self._cache.clear()
        self._timeouts.clear()
        self._file_mtimes.clear()

    async def watch_files(self, path: str, interval: int = 1):
        """Periodically check for file changes in the specified directory."""
        while True:
            await asyncio.sleep(interval)
            await self.check_files(path)

    async def check_files(self, path: str):
        """Check for file changes in the specified directory."""
        for root, _, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    mtime = os.path.getmtime(file_path)  # Get file modification time
                    if file_path not in self._file_mtimes:
                        # Add new file to cache
                        await self._cache_file(file_path)
                    elif mtime > self._file_mtimes[file_path]:
                        # Update cache if file has changed
                        await self._cache_file(file_path)
                except FileNotFoundError:
                    continue  # Skip if file is not found

    async def _cache_file(self, file_path: str):
        """Helper method to add or update a file in the cache."""
        async with aiofiles.open(file_path, 'rb') as f:
            content = await f.read()
        self.add(file_path, content)  # Add the file to cache
        self._file_mtimes[file_path] = os.path.getmtime(file_path)  # Update last modified time
        print(f"File cached: {file_path}")

    def start_watching(self, path: str, interval: int = 1):
        """Start watching files for changes."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.watch_files(path, interval))

    async def read_lines(self, file_path: typing.Optional[str] = None) -> typing.List[str]:
        """Read all lines from a file asynchronously."""
        path = configs.file_paths(file_path) if file_path else self.file_path
        async with self.lock:
            if not os.path.exists(path):
                return []

            async with aiofiles.open(path, 'r+', encoding='utf-8') as file:
                lines = await file.readlines()
                lines = [line.strip() for line in lines]  # Strip whitespace

                # Clear the content after reading
                await file.seek(0)
                await file.writelines([])
                await file.truncate()

            return lines

    async def write(self, content: str, file_path: typing.Optional[str] = None):
        """Write a string to a file asynchronously."""
        path = configs.file_paths(file_path) if file_path else self.file_path
        async with self.lock:
            async with aiofiles.open(path, 'a', encoding='utf-8') as file:
                await file.write(content + '\n')

    async def clear_file(
        self, dir_path: typing.Optional[str] = configs.DIR_CACHE
    ) -> None:
        """Delete all files in a specified directory asynchronously."""
        # Use the provided directory path or default to the object's file_path
        path = dir_path if dir_path else self.file_path

        # Ensure the path is a directory
        if not os.path.isdir(path):
            raise ValueError(f"{path} is not a valid directory")

        # Get all file names in the directory
        files = os.listdir(path)

        async with self.lock:
            for file_name in files:
                file_path = os.path.join(path, file_name)
                if os.path.isfile(file_path):
                    # Asynchronously delete the file
                    async with aiofiles.open(file_path, 'w', encoding='utf-8') as file:
                        await file.write("")  # Clear the content of the file
                    os.remove(file_path)  # Remove the empty file after clearing