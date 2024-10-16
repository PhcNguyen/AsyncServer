# `System` or `InternetProtocol`

## Giới thiệu
Đoạn mã này định nghĩa hai lớp: `System` và `InternetProtocol`. Lớp `System` cung cấp các chức năng để quản lý hệ thống, trong khi lớp `InternetProtocol` cung cấp các chức năng liên quan đến kết nối internet.

## Lớp `Colors`
### Mô tả
Lớp `Colors` cung cấp các phương thức để khởi tạo mã màu ANSI, cho phép in văn bản màu sắc trên terminal.

### Các thuộc tính
- **Màu sắc**: Các thuộc tính như `red`, `green`, `blue`,... đại diện cho các màu sắc khác nhau được khởi tạo bằng phương thức `start`.

## Lớp `System`
### Mô tả
Lớp này cung cấp các phương thức để thực hiện các tác vụ hệ thống như xóa màn hình, thực thi lệnh, reset ứng dụng, thoát ứng dụng, và kiểm tra mức sử dụng CPU và RAM.

### Các phương thức
- **`clear()`**: Xóa màn hình terminal.
- **`command(command: str)`**: Thực thi một lệnh hệ thống.
- **`reset()`**: Reset ứng dụng bằng cách thực thi lại script Python.
- **`exit()`**: Thoát ứng dụng.
- **`cpu()`**: Trả về tỷ lệ sử dụng CPU hiện tại.
- **`ram()`**: Trả về tỷ lệ sử dụng RAM hiện tại.
- **`sleep(seconds: float)`**: Tạm dừng thực thi trong một khoảng thời gian nhất định.
- **`dirtory(a: typing.LiteralString | str, *path: (typing.LiteralString | str))`**: Trả về đường dẫn kết hợp giữa thư mục và tên file.

## Lớp `InternetProtocol`
### Mô tả
Lớp này cung cấp các phương thức để lấy địa chỉ IP của máy, địa chỉ IP công cộng, và thực hiện lệnh ping để kiểm tra kết nối.

### Các thuộc tính
- **`param`**: Tham số cho lệnh ping, thay đổi theo hệ điều hành.
- **`host`**: Địa chỉ máy chủ để ping (mặc định là `google.com`).

### Các phương thức
- **`local()`**: Lấy địa chỉ IP cục bộ của máy tính.
- **`public()`**: Lấy địa chỉ IP công cộng từ dịch vụ bên ngoài.
- **`ping(timeout: int = 1)`**: Thực hiện lệnh ping đến máy chủ và trả về thời gian phản hồi.

## Ghi chú
- Sử dụng thư viện `psutil` để theo dõi mức sử dụng CPU và RAM.
- Sử dụng `requests` để truy cập địa chỉ IP công cộng.
- Các lỗi được xử lý và thông báo qua `print`.

## Giấy phép
Copyright (C) PhcNguyen Developers  
Distributed under the terms of the Modified BSD License.
