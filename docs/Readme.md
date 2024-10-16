## PhcNguyen Developers

Dự án này là một ứng dụng mạng bất đồng bộ, cho phép người dùng thực hiện các thao tác như đăng nhập, đăng ký và lấy thông tin người chơi. Ứng dụng sử dụng mã hóa RSA để bảo vệ dữ liệu người dùng và kết nối đến cơ sở dữ liệu để lưu trữ thông tin.

### Cấu trúc dự án
```structure
[PROJECT - 1.0.5]
  ├─── database                   # Thư mục chứa các tệp và thư mục liên quan đến cơ sở dữ liệu.
  │    ├───cache                  # Thư mục cho các tệp lưu trữ bộ nhớ đệm (cache).
  │    ├───data                   # Thư mục chứa dữ liệu chính của ứng dụng.
  │    ├───key                    # Thư mục chứa các tệp khóa, có thể là khóa mã hóa hoặc khóa RSA.
  │    ├───log                    # Thư mục lưu trữ các tệp log ghi lại thông tin hoạt động của ứng dụng.
  │    └───sql                    # Thư mục chứa các tệp SQL, có thể là các tệp để tạo hoặc cập nhật cơ sở dữ liệu.
  │
  ├─── docs                       # Thư mục chứa tài liệu hướng dẫn sử dụng hoặc tài liệu liên quan đến dự án.
  ├─── resource                   # Thư mục chứa các tài nguyên (resources) như phông chữ và biểu tượng.
  │    ├───font                   # Thư mục chứa các tệp phông chữ được sử dụng trong ứng dụng.
  │    └───icon                   # Thư mục chứa các biểu tượng (icon) cho ứng dụng.
  │
  ├─── sources                    # Thư mục chứa mã nguồn của ứng dụng.
  │    ├─── application           # Thư mục chứa các tệp liên quan đến ứng dụng, bao gồm các lệnh và cấu hình.
  │    ├─── manager               # Thư mục chứa các tệp quản lý, có thể là quản lý kết nối, quản lý cache, v.v.
  │    └─── model                 # Thư mục chứa các mô hình dữ liệu và logic xử lý.
  │        ├─── logging           # Thư mục chứa các tệp liên quan đến việc ghi log.
  │        └─── security          # Thư mục chứa các tệp liên quan đến bảo mật, mã hóa và giải mã dữ liệu.
  │             ├─── cipher       # Thư mục chứa các tệp xử lý mã hóa (cipher).
  │             └─── rsa          # Thư mục chứa các tệp xử lý liên quan đến RSA (mã hóa bất đối xứng).
  │
  ├─── env.sh                     # Tệp tạo môi trường ảo.
  └─── main.py                    # Tệp chính để khởi động ứng dụng.
```

---

#### 1. `AsyncNetworks`

- **Mô tả**: Class này quản lý các kết nối mạng và xử lý dữ liệu một cách không đồng bộ.
- **Phương thức**:
  - `start()`: Khởi động máy chủ và bắt đầu chấp nhận các kết nối.
  - `stop()`: Dừng máy chủ và đóng tất cả các kết nối.
  - `accept_connections()`: Chấp nhận các kết nối đến từ khách hàng.
  - `handle_client()`: Xử lý giao tiếp với khách hàng.

| Tính năng                             | V2                                                     |
|---------------------------------------|--------------------------------------------------------|
| **Loại mạng**                         | Không đồng bộ                                          |
| **Độ nhạy**                           | Độ đồng thời cao, ứng dụng thời gian thực              |
| **Độ phức tạp**                       | Phức tạp hơn, yêu cầu xử lý các cuộc gọi không đồng bộ |

#### 2. `AlgorithmProcessing`
- **Mô tả**: Xử lý dữ liệu từ client và thực hiện các thao tác liên quan đến tài khoản (đăng nhập, đăng ký).
- **Phương thức**:
  - `handle_data`: Xử lý dữ liệu từ client và trả về kết quả.
  - `close`: Đóng kết nối với cơ sở dữ liệu.

#### 3. `AsyncLogger`
- **Mô tả**: Ghi lại thông báo và lỗi một cách bất đồng bộ.
- **Phương thức**:
  - `notify`: Ghi thông báo.
  - `notify_error`: Ghi lỗi.

#### 4. `Cipher`
- **Mô tả**: Cung cấp chức năng mã hóa và giải mã dữ liệu bằng RSA.
- **Phương thức**:
  - `encrypt`: Mã hóa dữ liệu bằng khóa công khai.
  - `decrypt`: Giải mã dữ liệu bằng khóa riêng.

#### 5. `DatabaseManager`
- **Mô tả**: Quản lý các thao tác với cơ sở dữ liệu.
- **Phương thức**:
  - `insert_account`: Thêm tài khoản mới vào cơ sở dữ liệu.
  - `login`: Xác thực thông tin người dùng.
  - `get_player_coin`: Lấy số dư tiền ảo của người chơi.

#### 6. `Realtime`
- **Mô tả**: Cung cấp các phương thức liên quan đến thời gian.
- **Phương thức**:
  - `formatted_time`: Trả về thời gian hiện tại dưới định dạng `dd/mm/yy HH:MM`.
  - `timedelta`: Tạo đối tượng `timedelta` từ các tham số thời gian.

--- 

### Cách cài đặt

- Tạo môi trường ảo
  ```bash
      git clone https://github.com/PhcNguyen/Craps
      
      chmod +x venv.sh
      ./venv.sh
      ./venv.sh
      
      python main.py
  ```

- Cài đặt trực tiếp
  ```bash
      git clone https://github.com/PhcNguyen/Craps
      
      pip install -r requirements.txt
      python main.py
  ```