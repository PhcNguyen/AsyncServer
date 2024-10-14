-- queries.sql

-- --------------------------------------------------------
-- SELECT

SELECT * FROM account WHERE username = ?;              -- 1

SELECT password FROM account WHERE username = ?        -- 2

SELECT * FROM player WHERE name = ?;                   -- 3

SELECT coin, id FROM player WHERE name = ?;            -- 4

SELECT * FROM history WHERE id = ?;                    -- 5

SELECT * FROM history_transfer WHERE id = ?;           -- 6

-- --------------------------------------------------------
-- INSERT

INSERT INTO account (
    username, 
    password
) VALUES (?, ?);                                       -- 7

INSERT INTO player (
    name, 
    coin, 
    appellation, 
    last_login_time, 
    last_logout_time
) VALUES (?, ?, ?, ?, ?);                              -- 8

INSERT INTO history (
    id, 
    command, 
    timestamp, 
    ip_address
) VALUES (?, ?, CURRENT_TIMESTAMP, ?);                  -- 9

INSERT INTO history_transfer (
    id, 
    sender_name, 
    receiver_name, 
    amount, 
    message, 
    ip_address
) VALUES (?, ?, ?, ?, ?, ?);                            -- 10

-- --------------------------------------------------------
-- UPDATE

UPDATE account 
SET password = ?, update_time = CURRENT_TIMESTAMP 
WHERE username = ?;                                     -- 11

UPDATE player 
SET coin = ?, last_login_time = CURRENT_TIMESTAMP 
WHERE name = ?;                                         -- 12

UPDATE player 
SET last_login_time = CURRENT_TIMESTAMP 
WHERE name = ?;                                         -- 13

UPDATE player 
SET coin = coin + ?
WHERE name = ?;                                         -- 14

UPDATE player 
SET appellation = ? 
WHERE name = ?;                                         -- 15

-- --------------------------------------------------------
-- DELETE

DELETE FROM account 
WHERE id = ?;                                           -- 16

DELETE FROM player 
WHERE id = ?;                                           -- 17

DELETE FROM history 
WHERE id = ? AND timestamp = ?;                         -- 18

DELETE FROM history_transfer 
WHERE id = ? AND timestamp = ?;                         -- 19

-- --------------------------------------------------------
