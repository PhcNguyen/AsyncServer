# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import os
import asyncio
from src.security.cipher import Cipher
from src.client.config import ConfigClient


conf = ConfigClient.network_config()
host = conf[0]
port = conf[1]
del conf


class AsyncClient:
    def __init__(self):        
        self.server_address = (host, port)
        self.running = True
        self.cipher = Cipher(ConfigClient.key_path)

    async def connect(self):
        """Establish a connection to the server."""
        while self.running:
            try:
                reader, writer = await asyncio.open_connection(*self.server_address)
                return reader, writer  # Return the reader and writer to the caller
            except (ConnectionRefusedError, OSError) as e:
                await asyncio.sleep(5)  # Retry after 5 seconds

    async def handle_data(
        self, 
        message: bytes, 
        reader: asyncio.StreamReader, 
        writer: asyncio.StreamWriter
    ) -> list:
        """Send a message to the server and wait for a response."""
        responses = []  # List to accumulate decrypted responses
        try:
            encrypted_data = self.cipher.encrypt(message)
            
            if encrypted_data is None:  # Check if encryption was successful
                raise ValueError("Encryption failed: encrypted_data is None.")

            writer.write(encrypted_data)
            await writer.drain()  # Ensure the data is sent

            # Wait for a response from the server
            response = await reader.read(1024)
            if not response:
                return responses  # Return an empty list if the connection is closed
                
            # Handle response (assuming it's encrypted)
            decrypted_response = self.cipher.decrypt(response)
            responses.append(decrypted_response)  # Store the response

        finally:
            writer.close()
            await writer.wait_closed()
        return responses  # Return the accumulated responses


    def stop(self):
        self.running = False
