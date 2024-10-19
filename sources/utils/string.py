import random


class StringUtil:

    @staticmethod
    def random_text(length: int) -> str:
        """
        Tạo một chuỗi ngẫu nhiên có độ dài nhất định.

        :param length: Độ dài của chuỗi ngẫu nhiên cần tạo.
        :return: Chuỗi ngẫu nhiên được tạo ra.
        """
        left_limit = 48  # Giới hạn trái cho ký tự số '0'
        right_limit = 122  # Giới hạn phải cho ký tự chữ cái 'z'
        random_gen = random.Random()  # Tạo đối tượng Random

        # Tạo chuỗi ngẫu nhiên
        generated_string = ''.join(
            # Lấy các ký tự ngẫu nhiên từ left_limit đến right_limit
            chr(i) for i in random_gen.choices(
                range(left_limit, right_limit + 1),  # Giới hạn cho các ký tự
                k = length  # Số lượng ký tự cần lấy
            )
            # Lọc ra các ký tự hợp lệ (0-9, A-Z, a-z)
            if (48 <= i <= 57) or (65 <= i <= 90) or (97 <= i <= 122)
        )
        return generated_string
