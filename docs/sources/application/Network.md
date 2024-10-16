# AsyncNetworks

| Tính năng                             | V2                                                     |
|---------------------------------------|--------------------------------------------------------|
| **Loại mạng**                         | Không đồng bộ (`AsyncNetworks`)                        |
| **Độ nhạy**                           | Độ đồng thời cao, ứng dụng thời gian thực              |
| **Độ phức tạp**                       | Phức tạp hơn, yêu cầu xử lý các cuộc gọi không đồng bộ |

## Giới thiệu
Lớp `AsyncNetworks` kế thừa từ `Configs.Network` và được thiết kế để xử lý các kết nối mạng bất đồng bộ trong ứng dụng. Lớp này sử dụng `asyncio` để quản lý nhiều kết nối đồng thời, đồng thời tích hợp với tường lửa để bảo vệ server khỏi các kết nối không hợp lệ.

## Các thuộc tính

- **`MAX_CONNECTIONS`**: 
  - Số lượng kết nối tối đa (mặc định là 1000).

- **`stop_event`**: 
  - Sự kiện để dừng server.

- **`firewall`**: 
  - Đối tượng của lớp `FireWall`, dùng để quản lý các địa chỉ IP bị chặn.

- **`server_address`**: 
  - Địa chỉ server (host, port).

- **`algorithm`**: 
  - Đối tượng xử lý thuật toán, kế thừa từ `types.AlgorithmProcessing`.

- **`running`**: 
  - Trạng thái server (True nếu đang chạy, False nếu không).

- **`client_connections`**: 
  - Danh sách các kết nối khách hàng hiện tại.

## Các phương thức

### `__init__(host: str, port: int, algorithm: types.AlgorithmProcessing)`
Khởi tạo một đối tượng `AsyncNetworks` với địa chỉ `host`, `port` và thuật toán xử lý.

### `async def _close_connection(writer: asyncio.StreamWriter)`
Đóng kết nối của khách hàng.

### `def active_client()`
Trả về số lượng kết nối đang hoạt động.

### `async def start()`
Bắt đầu server và lắng nghe các kết nối đến một cách bất đồng bộ.

### `async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter)`
Xử lý dữ liệu từ một khách hàng một cách bất đồng bộ với thời gian chờ (timeout).

### `async def stop()`
Dừng server và đóng tất cả các kết nối một cách bất đồng bộ.

## Ghi chú
- Server hỗ trợ tái sử dụng cổng ngay lập tức thông qua tùy chọn `reuse_address`.
- Sử dụng tường lửa để chặn các địa chỉ IP không hợp lệ.
- Các lỗi và thông báo được ghi lại qua `AsyncLogger`.