# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

from typing import Dict, Callable, Union

from sources.utils import types
from sources.constants.cmd import Cmd, Codes
from sources.constants.result import ResultBuilder
from sources.handlers import PlayerHandler, AccountHandler
from sources.server.IO.transport import Transport



class TCPController:
    def __init__(self, database: Union[types.SQLite, types.MySQL], transport: Transport):
        self.database = database
        self.transport = transport

        # Initialize handlers for player and account operations
        self.player_handler = PlayerHandler(database)
        self.account_handler = AccountHandler(database)

        # Map command codes to their corresponding handler methods
        self.command_map: Dict[int, Callable] = {
            Cmd.LOGIN: self.account_handler.login,
            Cmd.LOGOUT: self.account_handler.logout,
            Cmd.REGISTER: self.account_handler.register,
            Cmd.PLAYER_INFO: self.player_handler.player_info,
            Cmd.PING: self.handle_ping,  # Add ping handling directly
        }

    async def send_error_response(self, code: int):
        """Send an error response to the client."""
        response = ResultBuilder.error(code)
        await self.transport.send(response)

    async def handle_ping(self):
        """Handle the PING command."""
        await self.transport.send(Cmd.PING)

    async def handle_command(self, code: int, command: Union[int, bytes], data) -> int:
        """
        Process incoming commands and return response codes.

        [0]: Disconnect
        [1]: Continue
        """
        print(code)
        # Handle special case codes for connection management
        if code == 3001:
            await self.send_error_response(code)
            return 0  # Disconnect after sending error response

        # Handle error codes and send responses accordingly
        if code in {2001, 5001, 4001, 4002, 6001, 6002}:
            await self.send_error_response(code)
            return 1  # Continue after sending error response

        # Handle disconnection codes
        if code in {1001, 5002, 5003, 5004}:
            return 0  # Disconnect immediately

        # Process regular commands
        handler = self.command_map.get(command)
        if callable(handler):
            await handler(data)
            return 1

        # If no handler found for the command, return error code
        await self.send_error_response(Codes.COMMAND_CODE_INVALID)
        return 1