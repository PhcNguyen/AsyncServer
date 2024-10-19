
-- Cơ sở dữ liệu: `server`

-- --------------------------------------------------------

--
-- Đang đổ dữ liệu cho bảng `account`
--

INSERT INTO `account` (`email`, `password`, `ban`, `role`, `active`, `create_time`) VALUES
('admin@example.com', '1', 0, 1, 0, '2022-02-19 10:44:33'),
('nguyen@example.com', '1', 0, 1, 0, '2022-02-19 10:46:22');

-- --------------------------------------------------------

--
-- Đang đổ dữ liệu cho bảng `player`
--

INSERT INTO `player` (
    `account_id`, `name`, `coin`, `gem`, `hp`, `mp`, `speed`, `damage`, `defense`, `crit`,
    `power`, `exp`, `position`, `item_body`, `item_bag`, `item_box`, `friends`, `data_task`,
    `max_luggage`, `level_bag`, `clan_id`, `character`, `description`, `updated_last`
)
VALUES
(1, 'admin', 1000, 1000, 100, 100, 1.0, 10, 0, 0, 100, 0, '0,0,0', '[]', '[]', '[]', '[]', '[]', 30, 0, -1, 0, NULL, '2024-10-12 18:53:52'),
(2, 'nguyen', 1000, 1000, 100, 100, 1.0, 10, 0, 0, 100, 0, '0,0,0', '[]', '[]', '[]', '[]', '[]', 30, 0, -1, 0, NULL, '2024-10-12 18:53:52');

-- --------------------------------------------------------

--
-- Đang đổ dữ liệu vào bảng `history`
--

INSERT INTO `history` (`account_id`, `action`, `timestamp`) VALUES
(1, 'login', '2024-10-12 08:00:00'),  -- Người dùng 1 đăng nhập
(1, 'logout', '2024-10-12 18:00:00'), -- Người dùng 1 đăng xuất
(2, 'login', '2024-10-12 09:00:00'),  -- Người dùng 2 đăng nhập
(2, 'logout', '2024-10-12 18:30:00'); -- Người dùng 2 đăng xuất

-- --------------------------------------------------------