import struct
from typing import Union, List, Any



class DataPackager:
    def __init__(self, encoding: str = 'utf-8'):
        self.encoding = encoding

    def encode(self, data: Union[str, int, float, List[Any]]) -> bytes:
        """Mã hóa dữ liệu thành bytes."""
        if isinstance(data, bytes):
            return data

        if isinstance(data, str):
            return data.encode(self.encoding)

        if isinstance(data, int):
            return struct.pack('!i', data)

        if isinstance(data, float):
            return struct.pack('!f', data)

        if isinstance(data, list):
            encoded_items = b''.join(self.encode(item) for item in data)
            return struct.pack('!i', len(encoded_items)) + encoded_items

        return (128).to_bytes(1)

    def decode(self, data: bytes) -> Union[str, int, float, List[Any]]:
        """Giải mã bytes về kiểu dữ liệu gốc."""
        if not data:
            raise ValueError("Dữ liệu không hợp lệ.")

        length = struct.unpack('!i', data[:4])[0]
        items = []
        offset = 4

        while offset < length + 4:
            item_type = data[offset:offset + 1]
            offset += 1

            if item_type == b's':  # Chuỗi
                str_length = struct.unpack('!i', data[offset:offset + 4])[0]
                offset += 4
                items.append(data[offset:offset + str_length].decode(self.encoding))
                offset += str_length
            elif item_type == b'i':  # Số nguyên
                items.append(struct.unpack('!i', data[offset:offset + 4])[0])
                offset += 4
            elif item_type == b'f':  # Số thực
                items.append(struct.unpack('!f', data[offset:offset + 4])[0])
                offset += 4
            else:
                raise ValueError("Kiểu dữ liệu không hợp lệ.")

        return items
