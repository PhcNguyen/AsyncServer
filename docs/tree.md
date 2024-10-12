# LANGUAGE
---
1. English
```
[ CRAPS - 1.0.31 ]
├───[ database ]            # This folder contains data storage and configuration files necessary for the game.
├───[ docs ]                # This folder holds documentation for the game, including user guides and development notes.
├───[ lib ]                 # This folder includes external libraries or custom libraries used in the project.
│      ├───Crypto           # A library for cryptographic functions, likely used for secure data handling.
│      ├───customtkinter    # A library for creating customized user interface components in Python applications.
│      └───pyasn1           # A library for handling ASN.1 data structures, typically used in network protocols.
├───[ src ]                 # This folder contains the main source code of the game.
│      ├───manager          # This module manages the game’s operations, such as starting, stopping, and handling player interactions.
│      ├───security         # This module includes security functions, providing encryption algorithms like AES and RSA.
│      │   ├───aes         # Implementation of the Advanced Encryption Standard (AES) for secure data encryption.
│      │   └───rsa          # Implementation of the RSA encryption algorithm, another method for secure data transmission.
│      └───server           # This module contains the main server code, processing requests from players.
├───[ test ]                # This folder includes test cases to ensure all functionalities of the game work correctly.
├─── server.py              # The main server file that likely initializes the game server and handles incoming connections.
└─── main.py                # The entry point of the application, responsible for starting the game and initializing the user interface.

```
---
2. Vietnamese
```
[ CRAPS - 1.0.31 ]
├───[ database ]            # Thư mục này chứa các tệp dữ liệu và cấu hình cần thiết cho trò chơi.
├───[ docs ]                # Thư mục này lưu trữ tài liệu hướng dẫn sử dụng và ghi chú phát triển cho trò chơi.
├───[ lib ]                 # Thư mục này bao gồm các thư viện bên ngoài hoặc thư viện tùy chỉnh được sử dụng trong dự án.
│      ├───Crypto           # Thư viện cho các chức năng mã hóa, có khả năng được sử dụng để xử lý dữ liệu an toàn.
│      ├───customtkinter    # Thư viện để tạo các thành phần giao diện người dùng tùy chỉnh trong các ứng dụng Python.
│      └───pyasn1           # Thư viện để xử lý các cấu trúc dữ liệu ASN.1, thường được sử dụng trong các giao thức mạng.
├───[ src ]                 # Thư mục này chứa mã nguồn chính của trò chơi.
│      ├───manager          # Mô-đun này quản lý các hoạt động của trò chơi, chẳng hạn như bắt đầu, dừng và xử lý tương tác của người chơi.
│      ├───security         # Mô-đun này bao gồm các chức năng bảo mật, cung cấp các thuật toán mã hóa như AES và RSA.
│      │   ├───aes         # Triển khai chuẩn mã hóa tiên tiến AES để mã hóa dữ liệu an toàn.
│      │   └───rsa          # Triển khai thuật toán mã hóa RSA, một phương pháp khác cho việc truyền dữ liệu an toàn.
│      └───server           # Mô-đun này chứa mã nguồn chính cho server, xử lý các yêu cầu từ người chơi.
├───[ test ]                # Thư mục này bao gồm các bài kiểm tra để đảm bảo tất cả các chức năng của trò chơi hoạt động đúng.
├─── server.py              # Tệp chính cho server, có khả năng khởi tạo server trò chơi và xử lý các kết nối đến.
└─── main.py                # Điểm vào của ứng dụng, chịu trách nhiệm khởi động trò chơi và khởi tạo giao diện người dùng.

```