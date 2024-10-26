# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.



class Cmd:
    LOGIN = 0           # Mã lệnh cho đăng nhập
    LOGOUT = 1          # Mã lệnh cho đăng xuất
    REGISTER = 2        # Mã lệnh cho đăng ký tài khoản
    PLAYER_INFO = 3     # Mã lệnh để lấy thông tin người chơi

    UPDATE = 5          # Mã lệnh để cập nhật
    DEAL = 6            # Mã lệnh để giao dịch


class Codes:
    # Mã thành công
    LOGIN_SUCCESS = 9001   # Đăng nhập thành công
    LOGOUT_SUCCESS = 9002  # Đăng xuất thành công

    # Mã lỗi
    COMMAND_CODE_INVALID = 6001   # Lệnh không hợp lệ
    ACCESS_DENIED = 6002          # Không có quyền truy cập
    MISSING_CREDENTIALS = 6008    # Thiếu thông tin đăng nhập
    LOGIN_TOO_FAST = 6005         # Đăng nhập quá nhanh
    ACCOUNT_ACTIVE = 6006         # Tài khoản đang hoạt động
    USER_ID_INVALID = 6007        # ID người dùng không hợp lệ
    TOKEN_REQUIRED = 6010         # Yêu cầu token
    TOKEN_INVALID = 6011          # Token không hợp lệ
    PLAYER_INFO_NOT_FOUND = 6009  # Không tìm thấy thông tin người chơi