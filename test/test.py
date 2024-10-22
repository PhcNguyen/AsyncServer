import asyncio

async def connect_to_server(host, port):
    reader, writer = await asyncio.open_connection(host, port)
    print(f'Connected to server at {host}:{port}')

    # Example to send and receive data
    writer.write(b'Hello, server!')
    await writer.drain()  # Wait until the data is sent
    print('Data sent to server.')

    # Close the connection
    writer.close()
    await writer.wait_closed()

if __name__ == '__main__':
    asyncio.run(connect_to_server('192.168.1.2', 7272))  # Change to server's IP if not local
