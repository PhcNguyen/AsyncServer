-- queries.sql

-- --------------------------------------------------------
-- SELECT

SELECT * FROM account
WHERE (id = ? OR email = ?)
AND (? IS NOT NULL OR ? IS NOT NULL);                  -- 1

SELECT name FROM sqlite_master WHERE type = 'table';   -- 2

SELECT * FROM player WHERE account_id = ?;             -- 3

SELECT * FROM player WHERE account_id = ?;             -- 4

SELECT * FROM history WHERE account_id = ?;            -- 5

SELECT * FROM history_transfer WHERE account_id = ?;   -- 6

;   -- 7
;   -- 8
;   -- 9
;   -- 10

;   -- 11
;   -- 12
;   -- 13
;   -- 14
;   -- 15
;   -- 16
;   -- 17
;   -- 18
;   -- 19
;   -- 20

-- --------------------------------------------------------
-- INSERT


INSERT INTO account (
    username, password
) VALUES (?, ?);                                       -- 21

INSERT INTO player (
    name
) VALUES (?);                                         -- 22

INSERT INTO history (
    id, action
) VALUES (?, ?);                                       -- 23

;   -- 24
;   -- 25
;   -- 26
;   -- 27
;   -- 28
;   -- 29
;   -- 30
;   -- 31
;   -- 32
;   -- 33
;   -- 34
;   -- 35
;   -- 36
;   -- 37
;   -- 38
;   -- 39
;   -- 40

-- --------------------------------------------------------
-- UPDATE

UPDATE account
SET password = ?
WHERE id = ?;                                          -- 41

UPDATE account
SET active = 1
WHERE id = ?;                                          -- 42

UPDATE account
SET active = 0
WHERE id = ?;                                          -- 43

UPDATE account
SET ban = 1
WHERE id = ? LIMIT 1;                                  -- 44

UPDATE account
SET ban = 0
WHERE id = ? LIMIT 1;                                  -- 45

UPDATE player
SET coin = ?
WHERE account_id = ?;                                  -- 46

UPDATE player
SET coin = coin + ?
WHERE account_id = ?;                                  -- 47

UPDATE player
SET {fields}
WHERE account_id = ?;                                  -- 48

UPDATE account
SET last_login = CURRENT_TIMESTAMP
WHERE email = ?;                                       -- 49
;   -- 50
;   -- 51
;   -- 52
;   -- 53
;   -- 54
;   -- 55
;   -- 56
;   -- 57
;   -- 58
;   -- 59
;   -- 60

-- --------------------------------------------------------
-- DELETE

DELETE FROM account
WHERE id = ?;                                         -- 61

DELETE FROM player
WHERE id = ?;                                         -- 62

DELETE FROM history
WHERE id = ?;                                         -- 63

DELETE FROM history_transfer
WHERE id = ? LIMIT 1;                                 -- 64

;   -- 65
;   -- 66
;   -- 67
;   -- 68
;   -- 69
;   -- 70

-- --------------------------------------------------------

SHOW TABLES; -- 71