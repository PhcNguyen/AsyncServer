# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import typing
import sqlite3

from models import settings



class MySQLite(settings.MySqlite):
    def __init__(
        self, db_path: str
    ) -> None:
        self.cur = None
        self.conn = None
        self.db_path = db_path
        self.message_callback = None

    def set_message_callback(self, callback):
        self.message_callback = callback

    def connection(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cur = self.conn.cursor()
        except sqlite3.OperationalError as e:
            self._notify_error(e)

    def close(self):
        if self.cur: self.cur.close()
        if self.conn: self.conn.close()

    def execute_query(self, query: str, params: tuple = None) -> typing.Any:
        """
        Thực thi một truy vấn SQL.
        
        :param query: Truy vấn SQL
        :param params: Tham số của truy vấn
        :return: Kết quả của truy vấn, hoặc None nếu có lỗi xảy ra
        """
        if self.cur:
            try:
                self.cur.execute(query, params or ())
                return self.cur.fetchall()
            except Exception as e:
                self._notify_error(f"Query failed: {e}")
                return None
        else:
            self._notify_error("Cursor is not initialized.")
            return None

    def register(self, username, password) -> bool:
        try:
            self.cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            self.conn.rollback()  # Rollback transaction on error
            return False

    def login(self, username, password):
        self.cur.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
        result = self.cur.fetchone()
        return result is not None

    def handle_message(self, sender, receiver, message) -> bool:
        # Check if sender is blocked by receiver
        self.cur.execute('''
            SELECT * FROM blocks
            WHERE user_id = (SELECT id FROM users WHERE username = ?)
            AND blocked_user_id = (SELECT id FROM users WHERE username = ?)
        ''', (receiver, sender))

        if self.cur.fetchone():
            return False  # Sender is blocked by receiver

        # Handle message logic here (save to DB or send to recipient)

        return True  # Message sent successfully

    def handle_friend_request(self, sender, receiver) -> bool:
        self.cur.execute("SELECT id FROM users WHERE username = ?", (receiver,))
        if self.cur.fetchone():
            self.cur.execute('''
                INSERT INTO friendships (user_id, friend_id, status)
                VALUES ((SELECT id FROM users WHERE username = ?), (SELECT id FROM users WHERE username = ?), 'pending')
            ''', (sender, receiver))
            self.conn.commit()
            return True  # Friend request sent
        else:
            return False  # Receiver does not exist

    def handle_accept_friend(self, sender, friend) -> bool:
        self.cur.execute('''
            UPDATE friendships SET status = 'accepted'
            WHERE user_id = (SELECT id FROM users WHERE username = ?)
            AND friend_id = (SELECT id FROM users WHERE username = ?)
            AND status = 'pending'
        ''', (friend, sender))
        self.conn.commit()

        # Check if a row was updated
        return self.cur.rowcount > 0  # True if request was accepted

    def handle_block_user(self, blocker, blockee) -> bool:
        self.cur.execute("SELECT id FROM users WHERE username = ?", (blockee,))
        if self.cur.fetchone():
            self.cur.execute('''
                INSERT INTO blocks (user_id, blocked_user_id)
                VALUES ((SELECT id FROM users WHERE username = ?), (SELECT id FROM users WHERE username = ?))
            ''', (blocker, blockee))
            self.conn.commit()
            return True  # User successfully blocked
        else:
            return False  # Blockee does not exist

    def _notify(self, message):
        """
        Notification method.
        """
        if self.message_callback:
            self.message_callback(f'Notify: {message}')

    def _notify_error(self, message):
        """
        Error notification method.
        """
        if self.message_callback:
            self.message_callback(f'Error: {message}')

    def create_all_tables(self):
        self.connection()
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT
                token TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            );
        """)
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS friendships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER REFERENCES users(id),
                friend_id INTEGER REFERENCES users(id),
                status TEXT CHECK (status IN ('pending', 'accepted', 'blocked'))
            );
        """)
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS blocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER REFERENCES users(id),
                blocked_user_id INTEGER REFERENCES users(id)
            );
        """)
        self.conn.commit()
        self.close()
