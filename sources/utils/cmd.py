# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

from enum import Enum



class Cmd(Enum):
    LOGIN = 0
    LOGOUT = 1
    REGISTER = 2
    PLAYER_INFO = 3

    UPDATE_APPELLATION = 4
    UPDATE_COIN = 5
    TRANSFER_COINS = 6

class MessageServer:
    pass

class MessageCode:
    messages = {
        500: "None",

        9001: "Đăng nhập thành công.",
        9002: "Đăng xuất thành công.",

        9501: "Dữ liệu đã gửi thành công",
        9502: "Dữ liệu đã nhận thành công",
    }

    @classmethod
    def get_message(cls, code: int) -> str:
        """Lấy thông điệp tương ứng với mã."""
        return cls.messages.get(code, "Mã không xác định.")


class ErrorCode:
    messages = {
        404: "Lỗi nghiêm trọng disconnected.",
        500: "None",
        # directory server
        1001: "Không có transport.",
        2001: "Lỗi khi giải mã JSON.",

        3001: "Lỗi timeout.",
        4001: "Lỗi khi giải mã Unicode.",
        4002: "Kiểu dữ liệu không được hỗ trợ.",

        5001: "Lỗi không xác định.",
        5002: "Lỗi mạng: Tên mạng được chỉ định không còn khả dụng.",
        5003: "Lỗi trong khi gửi.",
        5004: "Lỗi không mong muốn trong khi gửi",

        # file command.py
        6001: "Lệnh không hợp lệ.",
        6002: "Không có quyền truy cập.",
        6003: "Lỗi xử lý lệnh.",

        6004: "Thiếu email hoặc mật khẩu.",
        6005: "Bạn đã đăng nhập tài khoản quá nhanh. Vui lòng thử lại sau ít phút.",
        6006: "Tài khoản đang trực tuyến.",
        6007: "ID người dùng không hợp lệ.",
        6008: "Cần có email và mật khẩu.",
    }

    @classmethod
    def get_message(cls, code: int) -> str:
        """Lấy thông điệp tương ứng với mã lỗi."""
        return cls.messages.get(code, "Lỗi không xác định.")