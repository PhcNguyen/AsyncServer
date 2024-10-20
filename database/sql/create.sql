
-- Cơ sở dữ liệu: `server`

-- --------------------------------------------------------

-- Cấu trúc bảng cho bảng `account`
CREATE TABLE IF NOT EXISTS account (
    id INTEGER PRIMARY KEY AUTOINCREMENT,           -- Khóa chính, tự động tăng
    email TEXT NOT NULL UNIQUE,                      -- Địa chỉ email, duy nhất cho từng tài khoản
    password TEXT NOT NULL,                          -- Mật khẩu của tài khoản
    ban SMALLINT(1) DEFAULT 0,                       -- Trạng thái khóa tài khoản (0 cho không khóa, 1 cho khóa)
    role INTEGER DEFAULT 0,                          -- Quyền hạn của người dùng
    active BOOLEAN DEFAULT 0,                        -- Trạng thái trực tuyến của người dùng (0 cho không trực tuyến, 1 cho trực tuyến)
    last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Thời gian đăng nhập lần cuối
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP   -- Thời gian tạo bản ghi
);

-- --------------------------------------------------------

-- Cấu trúc bảng cho bảng `player`
CREATE TABLE IF NOT EXISTS player (
    id INTEGER PRIMARY KEY AUTOINCREMENT,            -- Khóa chính, tự động tăng
    account_id INTEGER NOT NULL,                     -- Khóa ngoại để liên kết với bảng account
    name TEXT NOT NULL UNIQUE,                       -- Tên nhân vật, duy nhất cho mỗi người chơi
    coin INTEGER DEFAULT 0,                          -- Số lượng tiền tệ của nhân vật
    gem INTEGER DEFAULT 0,                           -- Số lượng ngọc của nhân vật

    hp INTEGER NOT NULL DEFAULT 100,                 -- Điểm máu hiện tại (HP)
    mp INTEGER NOT NULL DEFAULT 100,                 -- Điểm ma lực hiện tại (MP)
    speed FLOAT NOT NULL DEFAULT 1,                  -- Tốc độ di chuyển của nhân vật
    damage INTEGER NOT NULL DEFAULT 10,              -- Sát thương của nhân vật
    defense INTEGER NOT NULL DEFAULT 0,              -- Phòng thủ của nhân vật
    crit INTEGER NOT NULL DEFAULT 0,                 -- Tỷ lệ chí mạng của nhân vật
    power INTEGER NOT NULL DEFAULT 100,              -- Sức mạnh của nhân vật
    exp INTEGER NOT NULL DEFAULT 0,                  -- Điểm kinh nghiệm của nhân vật
    position TEXT NOT NULL DEFAULT '0,0,0',          -- ID và tọa độ (id,x,y)
    item_body TEXT NOT NULL DEFAULT '[]',            -- Danh sách đồ trang bị
    item_bag TEXT NOT NULL DEFAULT '[]',             -- Danh sách đồ trong túi
    item_box TEXT NOT NULL DEFAULT '[]',             -- Danh sách đồ trong hộp
    friends TEXT NOT NULL DEFAULT '[]',              -- Danh sách bạn bè
    data_task TEXT NOT NULL DEFAULT '[]',            -- Dữ liệu nhiệm vụ
    max_luggage INTEGER NOT NULL DEFAULT 30,         -- Giới hạn trọng lượng tối đa, mặc định là 30
    level_bag INTEGER NOT NULL DEFAULT 0,            -- Cấp độ túi, mặc định là 0
    clan_id INTEGER DEFAULT -1,                      -- ID của bang hội (mặc định là -1 nếu không thuộc bang hội)
    character BIGINT DEFAULT '0',                    -- ID cho các bộ phận
    description TEXT DEFAULT NULL,                   -- Mô tả về nhân vật
    updated_last TIMESTAMP DEFAULT CURRENT_TIMESTAMP,-- Thời gian cập nhật
    FOREIGN KEY (account_id) REFERENCES account(id)  -- Thiết lập mối quan hệ khóa ngoại với bảng account
);

-- --------------------------------------------------------

-- Cấu trúc bảng cho bảng `player_bag`
CREATE TABLE IF NOT EXISTS player_bag (
    player_id INTEGER NOT NULL,                      -- ID của người chơi, khóa ngoại liên kết với bảng player
    item_id INTEGER NOT NULL DEFAULT -1,             -- ID của vật phẩm, mặc định là -1 nếu không có
    slot INTEGER NOT NULL,                           -- Vị trí trong túi (slot) để lưu trữ vật phẩm
    id INTEGER PRIMARY KEY AUTOINCREMENT             -- Khóa chính, tự động tăng
);

-- --------------------------------------------------------

-- Cấu trúc bảng cho bảng `clan`
CREATE TABLE IF NOT EXISTS clan (
    id INTEGER NOT NULL,                             -- Khóa chính, định danh duy nhất cho từng clan
    name VARCHAR(50) DEFAULT '',                     -- Tên của clan
    slogan VARCHAR(500) DEFAULT '',                  -- Khẩu hiệu của clan
    imgid INTEGER DEFAULT '0',                       -- ID hình ảnh đại diện của clan
    power BIGINT DEFAULT '0',                        -- Sức mạnh tổng của clan
    leadername VARCHAR(50) DEFAULT '',               -- Tên của người lãnh đạo clan
    currmember INTEGER DEFAULT '0',                  -- Số lượng thành viên hiện tại
    maxmember INTEGER DEFAULT '10',                  -- Số lượng tối đa thành viên có thể có
    date BIGINT DEFAULT '0',                         -- Ngày thành lập clan (dưới dạng timestamp)
    level INTEGER DEFAULT '1',                       -- Cấp độ của clan
    point INTEGER DEFAULT '0',                       -- Điểm của clan
    members LONGTEXT,                                -- Danh sách thành viên của clan
    messages LONGTEXT,                               -- Danh sách tin nhắn trong clan
    characterpeas LONGTEXT                           -- Danh sách các nhân vật của clan
);

-- --------------------------------------------------------

-- Cấu trúc bảng cho bảng `mob`
CREATE TABLE IF NOT EXISTS mob (
    id INTEGER PRIMARY KEY AUTOINCREMENT,            -- Khóa chính, tự động tăng
    name TEXT DEFAULT NULL,                          -- Tên của mob
    type INTEGER DEFAULT NULL,                       -- Loại mob
    range_move INTEGER DEFAULT NULL,                 -- Khoảng cách di chuyển của mob
    hp INTEGER DEFAULT NULL,                         -- Điểm sức khỏe của mob
    damage INTEGER NOT NULL,                         -- Sát thương của mob
    speed INTEGER DEFAULT NULL,                      -- Tốc độ di chuyển của mob
    darttype INTEGER DEFAULT NULL,                   -- Loại đạn mà mob sử dụng
    level INTEGER NOT NULL DEFAULT 10                -- Cấp độ của mob (mặc định là 10)
);

-- --------------------------------------------------------

-- Cấu trúc bảng cho bảng `store`
CREATE TABLE IF NOT EXISTS store (
    id INTEGER PRIMARY KEY,                         -- Cột id là khóa chính, kiểu INTEGER
    name TEXT,                                      -- Cột name lưu trữ tên mặt hàng
    type INTEGER,                                   -- Cột type lưu trữ loại cửa hàng
    shop TEXT,                                      -- Cột shop lưu trữ tên cửa hàng
    item TEXT                                       -- Cột item lưu trữ thông tin mặt hàng
);

-- --------------------------------------------------------

-- Cấu trúc bảng cho bảng `item`
CREATE TABLE IF NOT EXISTS item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,           -- Khóa chính, tự động tăng
    name TEXT NOT NULL,                             -- Tên vật phẩm
    type INTEGER NOT NULL,                          -- Loại vật phẩm
    coin INTEGER NOT NULL DEFAULT 0,                -- Số lượng xu yêu cầu
    gem INTEGER NOT NULL DEFAULT 0,                 -- Số lượng gem yêu cầu
    gender INTEGER NOT NULL,                        -- Giới tính phù hợp (0 cho nam, 1 cho nữ, 2 cho cả hai)
    description TEXT NOT NULL,                      -- Mô tả vật phẩm
    level INTEGER NOT NULL,                         -- Cấp độ yêu cầu để sử dụng vật phẩm
    power_require INTEGER NOT NULL,                 -- Sức mạnh yêu cầu để sử dụng vật phẩm
    icon_id INTEGER NOT NULL,                       -- ID biểu tượng của vật phẩm
    head INTEGER NOT NULL DEFAULT -1,               -- ID vật phẩm cho phần đầu
    body INTEGER NOT NULL DEFAULT -1,               -- ID vật phẩm cho phần thân
    leg INTEGER NOT NULL DEFAULT -1,                -- ID vật phẩm cho phần chân
    is_up_to_up BOOLEAN NOT NULL DEFAULT 0,         -- Trạng thái nâng cấp
    item_option TEXT NOT NULL DEFAULT '[]'          -- Tùy chọn vật phẩm
);

-- --------------------------------------------------------

-- Cấu trúc bảng cho bảng `itemsell`
CREATE TABLE IF NOT EXISTS itemsell (
    id INTEGER PRIMARY KEY AUTOINCREMENT,           -- Khóa chính, tự động tăng
    item TEXT NOT NULL,                             -- Tên vật phẩm được bán
    type INTEGER NOT NULL,                          -- Loại hình thanh toán
    coin INTEGER NOT NULL,                          -- Số tiền xu cần để mua vật phẩm
    gem INTEGER NOT NULL                            -- Số gem cần để mua vật phẩm

);

-- --------------------------------------------------------

-- Cấu trúc bảng cho bảng `event`
CREATE TABLE IF NOT EXISTS task (
    id INTEGER PRIMARY KEY AUTOINCREMENT,            -- Khóa chính, tự động tăng
    title TEXT NOT NULL,                             -- Tiêu đề sự kiện
    description TEXT NOT NULL,                       -- Mô tả sự kiện
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Thời gian bắt đầu sự kiện
    end_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP     -- Thời gian kết thúc sự kiện
);

-- --------------------------------------------------------

-- Cấu trúc bảng cho bảng `history`
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,           -- Tự động tăng ID cho từng bản ghi
    account_id INTEGER NOT NULL,                     -- ID tài khoản liên kết
    action TEXT NOT NULL,                            -- Hành động thực hiện
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,    -- Thời gian thực hiện hành động
    FOREIGN KEY (account_id) REFERENCES account(id)  -- Khóa ngoại liên kết với bảng account
);

-- --------------------------------------------------------

CREATE TRIGGER update_player_timestamp
AFTER UPDATE ON player
FOR EACH ROW
BEGIN
    UPDATE player
    SET updated_last = CURRENT_TIMESTAMP
    WHERE id = OLD.id;
END;

-- --------------------------------------------------------
