# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

from sources.utils.system import System



class Messages:
    # Define message categories
    MESSAGES = {
        # Success messages
        9001: "Đăng nhập thành công.",
        9002: "Đăng xuất thành công.",
        9501: "Dữ liệu đã gửi thành công.",
        9502: "Dữ liệu đã nhận thành công.",
        1000: "Pass",

        # Error messages

        1001: "Không có transport.",
        2001: "Lỗi không có dữ liệu.",
        3001: "Lỗi timeout.",
        4001: "Lỗi khi giải mã dữ liệu.",
        4002: "Kiểu dữ liệu không được hỗ trợ.",
        5001: "Lỗi không xác định.",
        5002: "Lỗi mạng: Tên mạng được chỉ định không còn khả dụng.",
        5003: "Lỗi trong khi gửi.",
        5004: "Lỗi không mong muốn trong khi gửi.",
        5005: "Không có dữ liệu nhận được.",
        6001: "Lệnh không hợp lệ.",
        6002: "Không có quyền truy cập.",
        6003: "Lỗi xử lý lệnh.",

        6004: "Thiếu email hoặc mật khẩu.",
        6005: "Bạn đã đăng nhập tài khoản quá nhanh. Vui lòng thử lại sau ít phút.",
        6006: "Tài khoản đang trực tuyến.",
        6007: "ID người dùng không hợp lệ.",
        6008: "Cần có email và mật khẩu.",
        6009: "Người chơi không tìm thấy.",
        6010: "Token là bắt buộc.",
        6011: "Token không hợp lệ."
    }

    @classmethod
    def get_message(cls, code: int) -> str:
        """Lấy thông điệp tương ứng với mã."""
        return cls.MESSAGES.get(code, "Lỗi không xác định.")

    @classmethod
    def check_duplicates(cls):
        """Check for duplicate codes in messages."""
        codes = set(cls.MESSAGES.keys())
        if len(codes) < len(cls.MESSAGES):
            duplicates = [code for code in cls.MESSAGES if list(cls.MESSAGES).count(code) > 1]
            print(f"Duplicate message codes found: {duplicates}")
            System.exit()  # Exit the program with a non-zero status code to indicate failure


if __name__ == "__main__":
    Messages.check_duplicates()  # This will check for duplicates and exit if found