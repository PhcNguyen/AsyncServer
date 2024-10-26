hân tích các cột trong bảng player
Cột	Kiểu Dữ Liệu	Kích Thước (bytes)	Mô Tả
id	INTEGER	4	Khóa chính, tự động tăng.
account_id	INTEGER	4	Khóa ngoại liên kết với bảng account.
name	TEXT	Tùy thuộc vào độ dài (giả sử 100 bytes)	Tên nhân vật, duy nhất cho mỗi người chơi.
coin	INTEGER	4	Số lượng tiền tệ của nhân vật.
gem	INTEGER	4	Số lượng ngọc của nhân vật.
hp	INTEGER	4	Điểm máu hiện tại (HP).
mp	INTEGER	4	Điểm ma lực hiện tại (MP).
speed	FLOAT	4	Tốc độ di chuyển của nhân vật.
damage	INTEGER	4	Sát thương của nhân vật.
defense	INTEGER	4	Phòng thủ của nhân vật.
crit	INTEGER	4	Tỷ lệ chí mạng của nhân vật.
power	INTEGER	4	Sức mạnh của nhân vật.
exp	INTEGER	4	Điểm kinh nghiệm của nhân vật.
position	TEXT	Tùy thuộc vào độ dài (giả sử 20 bytes)	ID và tọa độ (id,x,y).
item_body	TEXT	Tùy thuộc vào độ dài (giả sử 50 bytes)	Danh sách đồ trang bị.
item_bag	TEXT	Tùy thuộc vào độ dài (giả sử 50 bytes)	Danh sách đồ trong túi.
item_box	TEXT	Tùy thuộc vào độ dài (giả sử 50 bytes)	Danh sách đồ trong hộp.
friends	TEXT	Tùy thuộc vào độ dài (giả sử 100 bytes)	Danh sách bạn bè.
data_task	TEXT	Tùy thuộc vào độ dài (giả sử 100 bytes)	Dữ liệu nhiệm vụ.
max_luggage	INTEGER	4	Giới hạn trọng lượng tối đa, mặc định là 30.
level_bag	INTEGER	4	Cấp độ túi, mặc định là 0.
clan_id	INTEGER	4	ID của bang hội (mặc định là -1 nếu không thuộc bang hội).
character	BIGINT	8	ID cho các bộ phận.
description	TEXT	Tùy thuộc vào độ dài (giả sử 200 bytes)	Mô tả về nhân vật.
updated_last	TIMESTAMP	8	Thời gian cập nhật.
