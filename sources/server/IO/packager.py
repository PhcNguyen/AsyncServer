import struct
import json

class DataPackager:
    def __init__(self, encoding: str = 'utf-8'):
        self.encoding = encoding

    def encode(self, items: list) -> bytes:
        """Mã hóa danh sách các phần tử thành bytes."""
        encoded_data = b''

        for item in items:
            if isinstance(item, str):  # Chuỗi
                encoded_data += b's'  # Tiền tố xác định là chuỗi
                str_bytes = item.encode(self.encoding)
                encoded_data += struct.pack('!i', len(str_bytes))  # Độ dài chuỗi
                encoded_data += str_bytes  # Nội dung chuỗi
            elif isinstance(item, int):  # Số nguyên
                encoded_data += b'i'  # Tiền tố xác định là số nguyên
                encoded_data += struct.pack('!i', item)  # Giá trị số nguyên
            elif isinstance(item, float):  # Số thực
                encoded_data += b'f'  # Tiền tố xác định là số thực
                encoded_data += struct.pack('!f', item)  # Giá trị số thực
            elif isinstance(item, dict) or isinstance(item, list):  # JSON
                encoded_data += b'j'  # Tiền tố xác định là JSON
                json_bytes = json.dumps(item).encode(self.encoding)
                encoded_data += struct.pack('!i', len(json_bytes))  # Độ dài JSON
                encoded_data += json_bytes  # Nội dung JSON
            else:
                raise b'\x80'

        # Tiền tố tổng độ dài của dữ liệu
        total_length = struct.pack('!i', len(encoded_data))

        return total_length + encoded_data

    def decode(self, data: bytes):
        """Giải mã bytes về kiểu dữ liệu gốc."""
        if not data:
            return b'\x80'

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
            elif item_type == b'j':  # JSON
                json_length = struct.unpack('!i', data[offset:offset + 4])[0]
                offset += 4
                json_data = data[offset:offset + json_length].decode(self.encoding)
                items.append(json.loads(json_data))  # Chuyển đổi JSON về kiểu dữ liệu gốc
                offset += json_length
            else:
                raise b'\x80'

        return items
