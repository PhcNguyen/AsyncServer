# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import os
import typing
import aiofiles

from sources.utils.logger import AsyncLogger



class FileIO:
    @staticmethod
    def read_file(
            file: int | str | bytes | os.PathLike[str] | os.PathLike[bytes],
            mode: typing.Literal["r", "r+", "+r", "rt+", "r+t", "+rt", "tr+", "t+r", "+tr"] = "r",
            buffering: int = -1,
            encoding: str | None = 'utf-8',
            errors: str = 'ignore'
    ) -> str:
        """
        Reads the content of a file and returns it as a string.

        Parameters:
        file (int | str | bytes | os.PathLike[str] | os.PathLike[bytes]): The path to the file.
        buffering (int): Buffering policy. Default is -1, which means to use the default buffering.
        encoding (str | None): The encoding used to decode the file. Default is 'utf-8'.
        errors (str): The error handling scheme to use for decoding. Default is 'ignore'.

        Returns:
        str: The contents of the file. In case of error, an empty string is returned.
        """
        try:
            with open(file, mode=mode, buffering=buffering, encoding=encoding, errors=errors) as f:
                return f.read()
        except Exception as error:
            return str(error)

    @staticmethod
    def write_file(
            file: int | str | bytes | os.PathLike[str] | os.PathLike[bytes],
            content: str,
            mode: typing.Literal["w", "a", "x", "w+", "a+", "x+"] = "w",
            buffering: int = -1,
            encoding: str | None = 'utf-8',
            errors: str = 'ignore'
    ) -> bool:
        """
        Writes content to a file.

        Parameters:
        file (int | str | bytes | os.PathLike[str] | os.PathLike[bytes]): The path to the file.
        content (str): The content to write into the file.
        buffering (int): Buffering policy. Default is -1, which means to use the default buffering.
        encoding (str | None): The encoding used to decode the file. Default is 'utf-8'.
        errors (str): The error handling scheme to use for decoding. Default is 'ignore'.
        """
        try:
            with open(file, mode=mode, buffering=buffering, encoding=encoding, errors=errors) as f:
                f.write(content)
                return True
        except:
            return False

class AsyncFileIO:
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
        buffering (int): Buffering policy. Default is -1, which means to use the default buffering.
        encoding (str | None): The encoding used to decode the file. Default is 'utf-8'.
        errors (str): The error handling scheme to use for decoding. Default is 'ignore'.

        Returns:
        str: The contents of the file. In case of error, an empty string is returned.
        """
        try:
            async with aiofiles.open(
                file=file, mode=mode, buffering=buffering,
                    encoding=encoding, errors=errors
            ) as files:
                return await files.read()
        except Exception as error:
            await AsyncLogger.notify_error(error)
            return ""

    @staticmethod
    async def write_file(
        file: int | str | bytes | os.PathLike[str] | os.PathLike[bytes],
        content: str,
        mode: typing.Literal["w", "a", "x", "w+", "a+", "x+"] = "w",
        buffering: int = -1,
        encoding: str | None = 'utf-8',
        errors: str = 'ignore'
    ) -> None:
        """
        Asynchronously writes content to a file.

        Parameters:
        file (int | str | bytes | os.PathLike[str] | os.PathLike[bytes]): The path to the file.
        content (str): The content to write into the file.
        buffering (int): Buffering policy. Default is -1, which means to use the default buffering.
        encoding (str | None): The encoding used to decode the file. Default is 'utf-8'.
        errors (str): The error handling scheme to use for decoding. Default is 'ignore'.
        """
        try:
            async with aiofiles.open(
                file=file, mode=mode, buffering=buffering,
                    encoding=encoding, errors=errors
            ) as files:
                await files.write(content)
        except Exception as error:
            await AsyncLogger.notify_error(error)