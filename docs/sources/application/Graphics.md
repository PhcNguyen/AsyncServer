# Graphics

Lớp này kế thừa từ lớp `UIConfigs` và chịu trách nhiệm về các yếu tố trực quan và chức năng của ứng dụng. 

## Các thuộc tính
- **`server`**: Giữ thể hiện máy chủ.
- **`loop`**: Vòng lặp sự kiện `asyncio`.
- **Các hộp văn bản**: Dùng để hiển thị nhật ký.

## Các phương thức

### `_start_server`
- **Mô tả**: Khởi động máy chủ không đồng bộ, cập nhật nút bấm và chạy các tác vụ nền.

### `_stop_server`
- **Mô tả**: Dừng máy chủ không đồng bộ, cập nhật nút bấm và xóa thông tin máy chủ.

### `_update_server_infor`
- **Mô tả**: Cập nhật thông tin máy chủ như địa chỉ IP cục bộ và công cộng.

### `_auto_updater_infor`
- **Mô tả**: Cập nhật định kỳ việc sử dụng CPU, RAM, ping và số lượng kết nối (miễn là máy chủ đang chạy).

### `_auto_updater_message`
- **Mô tả**: Đọc và hiển thị các tin nhắn từ bộ nhớ cache không đồng bộ.

### `start_server`
- **Mô tả**: Khởi động máy chủ bằng `asyncio.run_coroutine_threadsafe`.

### `stop_server`
- **Mô tả**: Dừng máy chủ bằng `asyncio.run_coroutine_threadsafe`.

### `log_message`
- **Mô tả**: Nhận tin nhắn, phân loại chúng (Thông báo hoặc Lỗi) và hiển thị chúng trong hộp văn bản tương ứng.

### `clear_logs`
- **Mô tả**: Xóa tất cả các hộp văn bản hiển thị nhật ký.

### `on_closing`
- **Mô tả**: Xử lý đóng cửa sổ (dừng máy chủ nếu đang chạy, đóng vòng lặp sự kiện và hủy cửa sổ).
