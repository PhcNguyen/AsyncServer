# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import typing
import datetime
from sources.handlers.const import Messages


class ResultBuilder:
    @staticmethod
    def _create_response(
            status: str,
            code: typing.Union[int, None],
            message: str, **kwargs
    ) -> dict:
        """Helper method to create a standardized response dict."""
        response = {
            "status": status,
            "code": code,
            "message": message,
            "timestamp": datetime.datetime.now().isoformat()
        }
        response.update(kwargs)
        return response

    @staticmethod
    def success(code: int = 200, **kwargs) -> dict:
        """Return a dict with success status and a timestamp."""
        message = kwargs.get('message')

        if message is None:  # Check if message is not provided
            message = Messages.get_message(code) if code != 200 else "Operation completed successfully"
        return ResultBuilder._create_response('success', code, message, **kwargs)

    @staticmethod
    def error(code: int = 500, **kwargs) -> dict:
        """Return a dict with error status and a timestamp."""
        message = kwargs.get('message')

        if message is None:  # Check if message is not provided
            message = Messages.get_message(code) if code != 500 else "An error occurred"

        # Remove 'message' from kwargs to avoid conflict
        kwargs.pop('message', None)
        return ResultBuilder._create_response('error', code, message, **kwargs)

    @staticmethod
    def warning(**kwargs) -> dict:
        """Return a dict with warning status and a timestamp."""
        return ResultBuilder._create_response("warning", None, "", **kwargs)

    @staticmethod
    def info(**kwargs) -> dict:
        """Return a dict with info status and a timestamp."""
        return ResultBuilder._create_response("info", None, "", **kwargs)