import asyncio


async def send_requests(ip: str, port: int, message: str, num_requests: int):
    for _ in range(num_requests):
        reader, writer = await asyncio.open_connection(ip, port)

        try:
            writer.write(message.encode())
            await writer.drain()  # Đảm bảo rằng dữ liệu đã được gửi
            print(f"Sent message: {message}")
        except Exception as e:
            print(f"Error sending message: {e}")
        finally:
            writer.close()
            await writer.wait_closed()


async def main():
    ip = '192.168.1.2'  # Địa chỉ IP của server
    port = 7272  # Cổng của server
    message = 'Hello, Server!'  # Tin nhắn gửi đến server
    num_requests = 1000  # Số lượng yêu cầu gửi đến server

    await send_requests(ip, port, message, num_requests)


if __name__ == "__main__":
    asyncio.run(main())
