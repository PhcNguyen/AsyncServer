## <img alt="ICON"  src="https://github.com/PhcNguyen/AsyncServer/blob/main/resource/icon/graphics/0.ico" height="100px" width="auto"> PhcNguyen Developers 

Dự án này là một ứng dụng mạng bất đồng bộ, cho phép người dùng thực hiện các thao tác như đăng nhập, đăng ký và lấy thông tin người chơi. Ứng dụng sử dụng mã hóa RSA để bảo vệ dữ liệu người dùng và kết nối đến cơ sở dữ liệu để lưu trữ thông tin.

```structure
  ┌────[    1.0.7   ]────┐
  ├─── database          │ # Thư mục chứa các tệp và thư mục liên quan đến cơ sở dữ liệu.
  │    ├─── cache        │ # Thư mục cho các tệp lưu trữ bộ nhớ đệm (cache).
  │    ├─── data         │ # Thư mục chứa dữ liệu chính của ứng dụng.
  │    ├─── key          │ # Thư mục chứa các tệp khóa, có thể là khóa mã hóa hoặc khóa RSA.
  │    ├─── log          │ # Thư mục lưu trữ các tệp log ghi lại thông tin hoạt động của ứng dụng.
  │    └─── sql          │ # Thư mục chứa các tệp SQL, có thể là các tệp để tạo hoặc cập nhật cơ sở dữ liệu.
  │                      │
  ├─── docs              │ # Thư mục chứa tài liệu hướng dẫn sử dụng hoặc tài liệu liên quan đến dự án.
  ├─── resource          │ # Thư mục chứa các tài nguyên (resources) như phông chữ và biểu tượng.
  │    ├─── background   │ # Thư mục chứa các tệp hình nền.
  │    ├─── effect       │ # Thư mục chứa các hiệu ứng đồ họa.
  │    ├─── font         │ # Thư mục chứa các tệp phông chữ được sử dụng trong ứng dụng.
  │    └─── icon         │ # Thư mục chứa các biểu tượng (icon) cho ứng dụng.
  │                      │
  ├─── sources           │ # Thư mục chứa mã nguồn của ứng dụng.
  │    ├─── config       │ # Thư mục chứa các tệp liên quan đến ứng dụng, bao gồm các lệnh và cấu hình.
  │    ├─── handler      │ # Thư mục chứa các tệp quản lý, có thể là quản lý kết nối, quản lý cache, v.v.
  │    ├─── manager      │ # Thư mục chứa các mô hình dữ liệu và logic xử lý.
  │    ├─── model        │ # Thư mục chứa các mô hình dữ liệu.
  │    │   ├─── logging  │ # Thư mục chứa các tệp liên quan đến việc ghi log.
  │    │   └─── security │ # Thư mục chứa các tệp liên quan đến bảo mật, mã hóa và giải mã dữ liệu.
  │    ├─── server       │ # Thư mục chứa các tệp liên quan đến server.
  │    └─── ui           │ # Thư mục chứa các tệp liên quan đến giao diện người dùng.
  │                      │
  ├─── env.sh            │ # Tệp tạo môi trường ảo.
  ├─── main.py           │ # Tệp chính để khởi động ứng dụng.
  └──────────────────────┘
```

--- 

#### Cài đặt

- Tạo môi trường ảo

```bash
    git clone https://github.com/PhcNguyen/Craps
    
    chmod +x venv.sh
    ./venv.sh
```

- Chạy chương trình với GUI
```bash
    python main.py
```

- Chạy chương trình trên Terminal
```bash
    python main.py --nogui
```