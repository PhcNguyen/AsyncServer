from datetime import datetime
from sources.utils.cmd import ErrorCode, MessageCode



class ResponseBuilder:
    @staticmethod
    def success(code: int = 500, **kwargs) -> dict:
        """Trả về dict với trạng thái thành công kèm dấu thời gian."""
        message = kwargs.get('message') if code == 500 else MessageCode.get_message(code)

        response = {
            "status": True,
            "code": code,
            "message": message,  # Thêm thông điệp vào phản hồi
            "timestamp": datetime.now().isoformat()
        }
        response.update(kwargs)
        return response

    @staticmethod
    def error(code: int = 500, **kwargs) -> dict:
        """Trả về dict với trạng thái lỗi và mã lỗi."""
        message = kwargs.get('message') if code == 500 else ErrorCode.get_message(code)

        response = {
            "status": False,
            "code": code,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        response.update(kwargs)
        response.update(kwargs)
        return response

    @staticmethod
    def warning(**kwargs) -> dict:
        """Trả về dict với trạng thái cảnh báo."""
        response = {
            "status": "warning",
            "timestamp": datetime.now().isoformat()
        }
        response.update(kwargs)
        return response

    @staticmethod
    def info(**kwargs) -> dict:
        """Trả về dict với trạng thái thông tin."""
        response = {
            "status": "info",
            "timestamp": datetime.now().isoformat()}
        response.update(kwargs)
        return response