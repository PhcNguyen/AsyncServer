# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

from typing import Union
from datetime import datetime
from sources.handlers.const import Messages



class ResultBuilder:
    @staticmethod
    def _create_response(status: Union[bool, str], code: Union[int, None], message: str, **kwargs) -> dict:
        """Helper method to create a standardized response dict."""
        response = {
            "status": status,
            "code": code,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        response.update(kwargs)
        return response

    @staticmethod
    def success(code: int = 200, **kwargs) -> dict:
        """Return a dict with success status and a timestamp."""
        message = kwargs.get('message')
        if message is None:  # Check if message is not provided
            message = Messages.get_message(code) if code != 200 else "Operation completed successfully"
        return ResultBuilder._create_response(True, code, message, **kwargs)

    @staticmethod
    def error(code: int = 500, **kwargs) -> dict:
        """Return a dict with error status and a timestamp."""
        message = kwargs.get('message')
        if message is None:  # Check if message is not provided
            message = Messages.get_message(code) if code != 500 else "An error occurred"
        return ResultBuilder._create_response(False, code, message, **kwargs)

    @staticmethod
    def warning(**kwargs) -> dict:
        """Return a dict with warning status and a timestamp."""
        return ResultBuilder._create_response("warning", None, "", **kwargs)

    @staticmethod
    def info(**kwargs) -> dict:
        """Return a dict with info status and a timestamp."""
        return ResultBuilder._create_response("info", None, "", **kwargs)