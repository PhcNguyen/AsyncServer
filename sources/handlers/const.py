
from sources.utils.system import System


class Codes:
    # Success codes
    LOGIN_SUCCESS = 9001
    LOGOUT_SUCCESS = 9002

    # Error codes
    COMMAND_CODE_INVALID = 6001
    MISSING_CREDENTIALS = 6008
    LOGIN_TOO_FAST = 6005
    ACCOUNT_ACTIVE = 6006
    USER_ID_INVALID = 6007
    TOKEN_REQUIRED = 6010
    TOKEN_INVALID = 6011
    PLAYER_INFO_NOT_FOUND = 6009


class Messages:
    # Define message categories
    SUCCESS_MESSAGES = {
        9001: "Đăng nhập thành công.",
        9002: "Đăng xuất thành công.",
        9501: "Dữ liệu đã gửi thành công.",
        9502: "Dữ liệu đã nhận thành công.",
    }

    ERROR_MESSAGES = {
        404: "Lỗi nghiêm trọng disconnected.",
        1001: "Không có transport.",
        2001: "Lỗi khi giải mã JSON.",
        3001: "Lỗi timeout.",
        4001: "Lỗi khi giải mã Unicode.",
        4002: "Kiểu dữ liệu không được hỗ trợ.",
        5001: "Lỗi không xác định.",
        5002: "Lỗi mạng: Tên mạng được chỉ định không còn khả dụng.",
        5003: "Lỗi trong khi gửi.",
        5004: "Lỗi không mong muốn trong khi gửi.",
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
        if code in cls.SUCCESS_MESSAGES:
            return cls.SUCCESS_MESSAGES[code]

        elif code in cls.ERROR_MESSAGES:
            return cls.ERROR_MESSAGES[code]

        return "Lỗi không xác định."

    @classmethod
    def is_error_code(cls, code: int) -> bool:
        """Check if the provided code is an error code."""
        return code in cls.ERROR_MESSAGES

    @classmethod
    def is_success_code(cls, code: int) -> bool:
        """Check if the provided code is a success code."""
        return code in cls.SUCCESS_MESSAGES

    @classmethod
    def check_duplicates(cls):
        """Check for duplicate codes in success and error messages."""
        set(cls.SUCCESS_MESSAGES.keys()).union(set(cls.ERROR_MESSAGES.keys()))

        # Check for duplicates within success and error messages
        duplicates = {
            code for code in cls.SUCCESS_MESSAGES
            if code in cls.ERROR_MESSAGES
        }

        if duplicates:
            print(f"Duplicate message codes found: {duplicates}")
            System.exit()  # Exit the program with a non-zero status code to indicate failure



if __name__ == "__main__":
    Messages.check_duplicates()  # This will check for duplicates and exit if found