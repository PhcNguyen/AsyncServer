import os
import typing
import logging
import aiofiles



class FileIO:
    """Asynchronous file input/output operations."""

    @staticmethod
    async def read_file(
        file: int | str | bytes | os.PathLike[str] | os.PathLike[bytes],
        mode: typing.Literal["r", "r+", "+r", "rt+", "r+t", "+rt", "tr+", "t+r", "+tr"] = "r",
        buffering: int = -1,
        encoding: str | None = 'utf-8',
        errors: str = 'ignore'
    ) -> str:
        """
        Asynchronously reads the content of a file and returns it as a string.

        Parameters:
        file (int | str | bytes | os.PathLike[str] | os.PathLike[bytes]): The path to the file.
        mode (str): Mode for opening the file (default: 'r' for read).
        buffering (int): Buffering policy. Default is -1, which means to use the default buffering.
        encoding (str | None): The encoding used to decode the file. Default is 'utf-8'.
        errors (str): The error handling scheme for decoding. Default is 'ignore'.

        Returns:
        str: The contents of the file. In case of error, an empty string is returned.
        """
        try:
            async with aiofiles.open(file, mode=mode, buffering=buffering, encoding=encoding, errors=errors) as f:
                return await f.read()
        except Exception as error:
            logging.error(f"File-read error: {error}")
            return ""

    @staticmethod
    async def write_file(
        file: int | str | bytes | os.PathLike[str] | os.PathLike[bytes],
        content: str,
        mode: typing.Literal["w", "a", "x", "w+", "a+", "x+"] = "w",
        buffering: int = -1,
        encoding: str | None = 'utf-8',
        errors: str = 'ignore'
    ) -> bool:
        """
        Asynchronously writes content to a file.

        Parameters:
        file (int | str | bytes | os.PathLike[str] | os.PathLike[bytes]): The path to the file.
        content (str): The content to write into the file.
        mode (str): Mode for opening the file (default: 'w' for write).
        buffering (int): Buffering policy. Default is -1, which means to use the default buffering.
        encoding (str | None): The encoding used to encode the file. Default is 'utf-8'.
        errors (str): The error handling scheme for encoding. Default is 'ignore'.

        Returns:
        bool: True if the write operation was successful, False otherwise.
        """
        try:
            async with aiofiles.open(file, mode=mode, buffering=buffering, encoding=encoding, errors=errors) as f:
                await f.write(content)
            return True
        except Exception as error:
            logging.error(f"File-write error: {error}")
            return False