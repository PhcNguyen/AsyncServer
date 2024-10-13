

# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import asyncio

from src.server.graphics import Graphics
from src.server.mysqlite import DBManager
from src.server.networks import AsyncNetworks
from src.server.algorithm import AlgorithmHandler



# Initialize DatabaseManager, AsyncNetworks, and Graphics
sql = DBManager(DBManager.db_path)
async_networks = AsyncNetworks(AsyncNetworks.host, AsyncNetworks.port, AlgorithmHandler(sql))
app = Graphics(Graphics.root, async_networks)


# Periodically run the asyncio event loop within the Tkinter main loop
def run_asyncio_loop():
    """Run the asyncio event loop inside the Tkinter main loop without blocking."""
    try:
        # Run the asyncio event loop for a short time (non-blocking)
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(0.01))
    except Exception as e:
        print(f"Error in asyncio loop: {e}")
    Graphics.root.after(10, run_asyncio_loop)  # Call this function again after 10ms

# Start the async server as an asyncio task
async def start_network():
    await async_networks.start()  # This runs the server asynchronously

# Handle shutdown gracefully
async def stop_server():
    await async_networks.stop()  # Stop server asynchronously
    sql.close()  # Close database

# Function to stop the server when the window closes
def on_close():
    asyncio.create_task(stop_server())  # Run the stop server task
    Graphics.root.destroy()  # Close the GUI

# Bind the on_close function to the window close event
Graphics.root.protocol("WM_DELETE_WINDOW", on_close)

# Schedule the asyncio event loop to run in the Tkinter main loop
Graphics.root.after(10, run_asyncio_loop)

# Start the async network server
asyncio.create_task(start_network())

# Start the Tkinter main loop
Graphics.root.mainloop()
