-- MySqlite
-- Python version 3.12.5
--
-- Máy chủ: 127.0.0.1
-- Thời gian đã tạo: Th7 12, 2024 lúc 6:17 AM
-- Phiên bản máy phục vụ: 10.4.22-MariaDB

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

CREATE TABLE `account` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(20) NOT NULL,
  `password` varchar(100) NOT NULL,
  `create_time` timestamp NOT NULL DEFAULT current_timestamp(),
  `update_time` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `ip_address` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `account` (`id`, `username`, `password`, `create_time`, `update_time`, `ip_address`) VALUES
(1, 'admin', '1', '2022-02-19 10:44:33', '0000-00-00 00:00:00', '192.168.1.1'),
(2, 'nguyen', '1', '2022-02-19 10:46:22', '1979-12-31 11:01:01', '192.168.1.2');

CREATE TABLE `player` (
  `id` int(11) NOT NULL,
  `name` varchar(20) NOT NULL,
  `coin` int(11) NOT NULL DEFAULT 0,
  `appellation` varchar(50) NOT NULL,
  `last_login_time` timestamp NOT NULL DEFAULT '1979-12-31 11:01:01',
  `last_logout_time` timestamp NOT NULL DEFAULT '1979-12-31 11:01:01',
  `ip_address` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `player` (`id`, `name`, `coin`, `appellation`, `last_login_time`, `last_logout_time`, `ip_address`) VALUES
(1, 'admin', 1000, 'ADMIN', '1979-12-31 11:01:01', '2024-10-12 18:53:52', '192.168.1.1'),
(2, 'nguyen', 1200, 'ADMIN', '1979-12-31 11:01:01', '2024-10-12 18:53:52', '192.168.1.2');

CREATE TABLE `history` (
  `id` int(11) NOT NULL,
  `action` varchar(50) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp(),
  `ip_address` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`id`) REFERENCES `account`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `history` (`id`, `action`, `timestamp`, `ip_address`) VALUES
(1, 'login', '2024-10-12 08:00:00', '192.168.1.1'),
(1, 'logout', '2024-10-12 18:00:00', '192.168.1.1'),
(2, 'login', '2024-10-12 09:00:00', '192.168.1.2'),
(2, 'logout', '2024-10-12 18:30:00', '192.168.1.2');

COMMIT;
