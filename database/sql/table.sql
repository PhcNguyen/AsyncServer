-- Python version 3.12.5
--
-- Máy chủ: 127.0.0.1
-- Thời gian đã tạo: Th7 12, 2024 lúc 6:17 AM

--
-- Cơ sở dữ liệu: `server`
--

-- --------------------------------------------------------

-- 
-- Cấu trúc bảng cho bảng `account`
--

CREATE TABLE IF NOT EXISTS account (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,               -- Địa chỉ email, duy nhất cho từng tài khoản
    password TEXT NOT NULL,                   -- Mật khẩu của tài khoản
    is_lock BOOLEAN DEFAULT 0,                -- Trạng thái khóa tài khoản (0 cho không khóa, 1 cho khóa)
    role INTEGER DEFAULT 0,                   -- Quyền hạn của người dùng
    is_online BOOLEAN DEFAULT 0,              -- Trạng thái trực tuyến của người dùng (0 cho không trực tuyến, 1 cho trực tuyến)
    is_login BOOLEAN DEFAULT 0,               -- Trạng thái đăng nhập (0 cho không đăng nhập, 1 cho đăng nhập)
    phone_number TEXT DEFAULT NULL,           -- Số điện thoại của người dùng (có thể để trống)
    last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Thời gian đăng nhập lần cuối
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_last TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP -- Cập nhật thời gian khi có thay đổi
);

-- --------------------------------------------------------

-- 
-- Cấu trúc bảng cho bảng `player`
--

CREATE TABLE IF NOT EXISTS player (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,  -- Khóa ngoại để liên kết với bảng account
    name TEXT NOT NULL UNIQUE,

    power INTEGER NOT NULL DEFAULT 100,
    hp INTEGER NOT NULL DEFAULT 100,
    mp INTEGER NOT NULL DEFAULT 100,
    damage INTEGER NOT NULL DEFAULT 10,
    defense INTEGER NOT NULL DEFAULT 0,
    crit INTEGER NOT NULL DEFAULT 0,
    exp INTEGER NOT NULL DEFAULT 0,

    coin INTEGER DEFAULT 0,
    gem INTEGER DEFAULT 0,

    character bigint(20) DEFAULT '0',
    description TEXT DEFAULT NULL,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_last TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES account(id)  -- Thiết lập mối quan hệ khóa ngoại
);

-- --------------------------------------------------------

-- 
-- Cấu trúc bảng cho bảng `history`
--

CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Tự động tăng cho ID của lịch sử
    account_id INTEGER NOT NULL,            -- Khóa ngoại để liên kết với bảng account
    command TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES account(id) ON DELETE CASCADE  -- Thiết lập mối quan hệ khóa ngoại
);

-- --------------------------------------------------------

-- 
-- Cấu trúc bảng cho bảng `history_transfer`
--

CREATE TABLE IF NOT EXISTS history_transfer (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,  -- Khóa ngoại để liên kết với bảng account
    sender_name TEXT NOT NULL,
    receiver_name TEXT NOT NULL,
    amount INTEGER NOT NULL,
    message TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES account(id) ON DELETE CASCADE  -- Thiết lập mối quan hệ khóa ngoại
);

-- --------------------------------------------------------

-- 
-- Đang đổ dữ liệu cho bảng `account`
--

INSERT INTO `account` (`username`, `password`, `is_lock`, `role`, `is_online`, `create_time`, `update_time`) VALUES
('admin', '1', 0, 1, 0, '2022-02-19 10:44:33', '0000-00-00 00:00:00'),
('nguyen', '1', 0, 1, 0,  '2022-02-19 10:46:22', '1979-12-31 11:01:01');

-- --------------------------------------------------------

-- 
-- Đang đổ dữ liệu cho bảng `player`
--

INSERT INTO `player` (`account_id`, `name`, `coin`, `character`, `last_login_time`, `last_logout_time`) VALUES
(1, 'admin', 1000, 0, '2024-10-12 08:00:00', '2024-10-12 18:53:52'),
(2, 'nguyen', 1200,0 , '2024-10-12 09:00:00', '2024-10-12 18:53:52');

-- --------------------------------------------------------

-- 
-- Đang đổ dữ liệu vào bảng `history`
--

INSERT INTO `history` (`account_id`, `command`, `timestamp`) VALUES
(1, 'login', '2024-10-12 08:00:00'),  -- Người dùng 1 đăng nhập
(1, 'logout', '2024-10-12 18:00:00'), -- Người dùng 1 đăng xuất
(2, 'login', '2024-10-12 09:00:00'),  -- Người dùng 2 đăng nhập
(2, 'logout', '2024-10-12 18:30:00'); -- Người dùng 2 đăng xuất

-- --------------------------------------------------------

--
-- Đang đổ dữ liệu vào bảng `history_transfer`
--

INSERT INTO history_transfer (account_id, sender_name, receiver_name, amount, message) VALUES
(1, 'admin', 'nguyen', 500, 'Transfer for game purchase'),
(2, 'nguyen', 'admin', 300, 'Thanks for the gift!'),
(1, 'admin', 'nguyen', 200, 'Transfer for lunch'),
(2, 'nguyen', 'admin', 150, 'Payment for the bet');

-- --------------------------------------------------------
COMMIT;