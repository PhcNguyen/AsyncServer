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
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- --------------------------------------------------------

-- 
-- Cấu trúc bảng cho bảng `player`
--

CREATE TABLE IF NOT EXISTS player (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,  -- Khóa ngoại để liên kết với bảng account
    name TEXT NOT NULL UNIQUE,
    coin INTEGER DEFAULT 0,
    appellation TEXT NOT NULL,
    last_login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_logout_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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

INSERT INTO `account` (`username`, `password`, `create_time`, `update_time`) VALUES
('admin', '1', '2022-02-19 10:44:33', '0000-00-00 00:00:00'),
('nguyen', '1', '2022-02-19 10:46:22', '1979-12-31 11:01:01');

-- --------------------------------------------------------

-- 
-- Đang đổ dữ liệu cho bảng `player`
--

INSERT INTO `player` (`account_id`, `name`, `coin`, `appellation`, `last_login_time`, `last_logout_time`) VALUES
(1, 'admin', 1000, 'ADMIN', '2024-10-12 08:00:00', '2024-10-12 18:53:52'),
(2, 'nguyen', 1200, 'ADMIN', '2024-10-12 09:00:00', '2024-10-12 18:53:52');

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