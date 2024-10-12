# CRAPS PROJECT
## Structure
```
[ CRAPS - 1.0.31 ]
├───[ database ]
├───[ docs ]
├───[ lib ]
│      ├───Crypto
│      ├───customtkinter
│      └───pyasn1
├───[ src ]
│      ├───manager
│      ├───security
│      │   ├───aes
│      │   └───rsa
│      └───server
├───[ test ]
├─── server.py
└─── main.py
```

---

## Language

--- 

### 1. English
- **[ CRAPS - 1.0.31 ]**: The name of the dice game project.

- **[ database ]**: This folder contains the data files and configurations required for the game.

- **[ docs ]**: This folder stores the user manual and development notes for the game.

- **[ lib ]**: This folder includes external libraries or custom libraries used in the project.
  - **Crypto**: Library for encryption functions, potentially used for secure data processing.
  - **customtkinter**: A library for creating custom UI components in Python applications.
  - **pyasn1**: Library for processing ASN.1 data structures, commonly used in network protocols.

- **[ src ]**: This folder contains the game's main source code.
  - **manager**: This module manages game activities, such as starting, stopping, and handling player interactions.
  - **security**: This module includes security functions, providing encryption algorithms such as AES and RSA.
    - **AES**: Implements the advanced encryption standard AES to encrypt data securely.
    - **RSA**: Implements the RSA encryption algorithm, another method for secure data transmission.
  - **server**: This module contains the main source code for the server, which handles requests from players.

- **[ test ]**: This folder contains tests to ensure all the functions of the game are working properly.

- **server.py**: The main file for the server, capable of initializing the game server and handling incoming connections.

- **main.py**: The entry point of the application, which is responsible for launching the game and initializing the user interface.

---

### 2. Vietnamese
- **[ CRAPS - 1.0.31 ]**: Tên của dự án trò chơi xúc xắc.

- **[ database ]**: Thư mục này chứa các tệp dữ liệu và cấu hình cần thiết cho trò chơi.

- **[ docs ]**: Thư mục này lưu trữ tài liệu hướng dẫn sử dụng và ghi chú phát triển cho trò chơi.

- **[ lib ]**: Thư mục này bao gồm các thư viện bên ngoài hoặc thư viện tùy chỉnh được sử dụng trong dự án.
  - **Crypto**: Thư viện cho các chức năng mã hóa, có khả năng được sử dụng để xử lý dữ liệu an toàn.
  - **customtkinter**: Thư viện để tạo các thành phần giao diện người dùng tùy chỉnh trong các ứng dụng Python.
  - **pyasn1**: Thư viện để xử lý các cấu trúc dữ liệu ASN.1, thường được sử dụng trong các giao thức mạng.

- **[ src ]**: Thư mục này chứa mã nguồn chính của trò chơi.
  - **manager**: Mô-đun này quản lý các hoạt động của trò chơi, chẳng hạn như bắt đầu, dừng và xử lý tương tác của người chơi.
  - **security**: Mô-đun này bao gồm các chức năng bảo mật, cung cấp các thuật toán mã hóa như AES và RSA.
    - **aes**: Triển khai chuẩn mã hóa tiên tiến AES để mã hóa dữ liệu an toàn.
    - **rsa**: Triển khai thuật toán mã hóa RSA, một phương pháp khác cho việc truyền dữ liệu an toàn.
  - **server**: Mô-đun này chứa mã nguồn chính cho server, xử lý các yêu cầu từ người chơi.

- **[ test ]**: Thư mục này bao gồm các bài kiểm tra để đảm bảo tất cả các chức năng của trò chơi hoạt động đúng.

- **server.py**: Tệp chính cho server, có khả năng khởi tạo server trò chơi và xử lý các kết nối đến.

- **main.py**: Điểm vào của ứng dụng, chịu trách nhiệm khởi động trò chơi và khởi tạo giao diện người dùng.
