# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import os
import typing
import asyncio
import aiofiles

from sources.manager import iofiles
from sources.application.configs import Configs



class Cache:
    def __init__(self):
        self.file_path = Configs.FILE_PATHS["temp.cache"]
        self.lock = asyncio.Lock()  # Async lock for thread safety

    async def read_lines(self) -> typing.List[str]:
        """Read all lines from the file and return them as a list."""
        async with self.lock:  # Ensure thread-safe access
            if not os.path.exists(self.file_path):
                return []

            async with aiofiles.open(self.file_path, 'r+', encoding='utf-8') as file:
                lines = await file.readlines()
                if not lines:
                    return []

                # Remove leading/trailing whitespace characters from each line
                lines = [line.strip() for line in lines]

                # Clear the file after reading
                await file.seek(0)
                await file.writelines(lines[0:0])  # Clear the file by writing empty lines
                await file.truncate()  # Truncate the rest of the content

            return lines

    async def write(self, string: str) -> None:
        """Write a line to the file."""
        async with self.lock:  # Ensure thread-safe access
            # Add the new line to the file
            await iofiles.write_files(self.file_path, (string + '\n'), mode='a')

    async def clear(self) -> None:
        """Clear all content from the cache file."""
        async with self.lock:  # Ensure thread-safe access
             # Write an empty string to clear the content
            await iofiles.write_files(self.file_path, content="", mode='a')