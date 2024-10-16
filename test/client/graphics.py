# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import asyncio
import customtkinter as ctk
from test.client.config import ConfigClient
from test.client.networks import AsyncClient  # Import your AsyncClient class here



class AuthMenu:
    root = ctk.CTk()

    def __init__(self, master):
        self.master = master
        self.master.title("CRAPS")
        self.master.geometry("400x400")  # Set window size

        # Initialize AsyncClient with server details
        self.client = AsyncClient()  # Adjust host and port as needed

        # Read IP address from configuration file
        self.ip_address = ConfigClient.network_config()[0]

        self.create_main_menu()

    def create_main_menu(self):
        """Create the main menu with options for login, register, and server selection."""
        # Clear the window
        self.clear_widgets()

        # Title Label
        title_label = ctk.CTkLabel(self.master, text="CRAPS", font=("Arial", 24))
        title_label.pack(pady=(20, 10))  # More padding at the top

        # Server IP Address Label
        ip_label = ctk.CTkLabel(self.master, text=f"Server IP: {self.ip_address}", font=("Arial", 16))
        ip_label.pack(pady=(0, 20))  # Padding below the label

        # Login Button
        login_button = ctk.CTkButton(self.master, text="Login", command=self.show_login)
        login_button.pack(pady=(0, 10), padx=20, fill="x")  # Fill the button horizontally

        # Register Button
        register_button = ctk.CTkButton(self.master, text="Register", command=self.show_register)
        register_button.pack(pady=(0, 20), padx=20, fill="x")  # Fill the button horizontally

        # Status Label
        self.status_label = ctk.CTkLabel(self.master, text="")
        self.status_label.pack(pady=(0, 5))

    def show_login(self):
        """Show the login screen."""
        self.clear_widgets()

        # Title Label
        title_label = ctk.CTkLabel(self.master, text="Login", font=("Arial", 24))
        title_label.pack(pady=(20, 10))

        # Username Entry
        self.username_entry = ctk.CTkEntry(self.master, placeholder_text="Username")
        self.username_entry.pack(pady=(0, 5), padx=20, fill="x")  # Fill the entry horizontally

        # Password Entry
        self.password_entry = ctk.CTkEntry(self.master, placeholder_text="Password", show='*')
        self.password_entry.pack(pady=(0, 5), padx=20, fill="x")

        # Login Button
        login_button = ctk.CTkButton(self.master, text="Login", command=self.handle_login)
        login_button.pack(pady=(0, 10), padx=20, fill="x")

        # Back Button
        back_button = ctk.CTkButton(self.master, text="Back", command=self.create_main_menu)
        back_button.pack(pady=(0, 20), padx=20, fill="x")

        # Status Label
        self.status_label = ctk.CTkLabel(self.master, text="")
        self.status_label.pack(pady=(0, 5))

    def show_register(self):
        """Show the registration screen."""
        self.clear_widgets()

        # Title Label
        title_label = ctk.CTkLabel(self.master, text="Register", font=("Arial", 24))
        title_label.pack(pady=(20, 10))

        # Username Entry
        self.username_entry = ctk.CTkEntry(self.master, placeholder_text="Username")
        self.username_entry.pack(pady=(0, 5), padx=20, fill="x")

        # Password Entry
        self.password_entry = ctk.CTkEntry(self.master, placeholder_text="Password", show='*')
        self.password_entry.pack(pady=(0, 5), padx=20, fill="x")

        # Register Button
        register_button = ctk.CTkButton(self.master, text="Register", command=self.handle_register)
        register_button.pack(pady=(0, 10), padx=20, fill="x")

        # Back Button
        back_button = ctk.CTkButton(self.master, text="Back", command=self.create_main_menu)
        back_button.pack(pady=(0, 20), padx=20, fill="x")

        # Status Label
        self.status_label = ctk.CTkLabel(self.master, text="")
        self.status_label.pack(pady=(0, 5))

    def clear_widgets(self):
        """Clear all widgets in the current frame."""
        for widget in self.master.winfo_children():
            widget.destroy()

    async def send_request(self, command: int):
        """Send login or registration request to the server."""
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Prepare the message to send
        message = {'command': command, 'username': username, 'password': password}
        message_bytes = bytes(str(message), 'utf-8')

        # Create a connection to the server
        reader, writer = await self.client.connect()

        try:
            # Await the response from the server
            response = await self.client.handle_data(message_bytes, reader, writer)

            # Process the response
            if response and response[0].get("status") == "success":
                self.status_label.configure(text=f"{'Login' if command == 0 else 'Register'} successful!", text_color="green")
                # Proceed to the next part of the game or application
            else:
                self.status_label.configure(text="Error: " + response[0].get("message", "Unknown error"), text_color="red")

        finally:
            # Close the connection
            writer.close()
            await writer.wait_closed()



    def handle_login(self):
        """Handle the login button click."""
        asyncio.run(self.send_request(0))  # Pass command 0 for login

    def handle_register(self):
        """Handle the register button click."""
        asyncio.run(self.send_request(1))  # Pass command 1 for register

# Run the application
if __name__ == "__main__":
    app = AuthMenu(AuthMenu.root)
    app.root.mainloop()
