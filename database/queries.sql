-- queries.sql

-- --------------------------------------------------------
-- SELECT

SELECT * FROM account WHERE username = ?;       -- 1

SELECT * FROM player WHERE id = ?;              -- 2

SELECT * FROM history WHERE id = ?;             -- 3

SELECT * FROM history_transfer WHERE id = ?;    -- 4

-- --------------------------------------------------------
-- INSERT

INSERT INTO account (username, password) VALUES (?, ?); -- 5

INSERT INTO player (
    name, 
    coin, 
    appellation, 
    last_login_time, 
    last_logout_time
) VALUES (?, ?, ?, ?, ?); -- 6

INSERT INTO history (
    id, 
    command, 
    timestamp, 
    ip_address
) VALUES (?, ?, CURRENT_TIMESTAMP, ?); -- 7

INSERT INTO history_transfer (
    id, 
    sender_name, 
    receiver_name, 
    amount, 
    message, 
    ip_address
) VALUES (?, ?, ?, ?, ?, ?); -- 8

-- --------------------------------------------------------
-- UPDATE

UPDATE account 
SET password = ?, update_time = CURRENT_TIMESTAMP 
WHERE username = ?;

UPDATE player 
SET coin = ?, last_login_time = CURRENT_TIMESTAMP 
WHERE id = ?;

UPDATE player 
SET last_login_time = CURRENT_TIMESTAMP 
WHERE id = ?;

-- --------------------------------------------------------
-- DELETE

DELETE FROM account WHERE id = ?;

DELETE FROM player WHERE id = ?;

DELETE FROM history WHERE id = ? AND timestamp = ?;

DELETE FROM history_transfer WHERE id = ? AND timestamp = ?;

-- --------------------------------------------------------
