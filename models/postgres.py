
# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import json
import typing
import psycopg2

from psycopg2 import OperationalError, extensions
from models import settings



class Postgres(settings.Postgres):
    def __init__(
        self, host: str, 
        port: int, dbname: str, 
        user: str, password: str,
    ) -> None:
        self.cur = None
        self.conn = None
        self.host = host
        self.port = port
        self.user = user
        self.dbname = dbname
        self.password = password
        self.message_callback = None
    
    def set_message_callback(self, callback):
        self.message_callback = callback
        
    def connection(self):
        try:
            self.conn: extensions.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                dbname=self.dbname,
                user=self.user,
                password=self.password
            )
            self.cursor: extensions.cursor = self.conn.cursor()
        except OperationalError as e:
            self._notify_error(e)
    
    def close(self):
        if self.cursor: self.cursor.close()
        if self.conn: self.conn.close()

    def execute_query(self, query: str, params: tuple = None) -> typing.Any:
        """
        Thực thi một truy vấn SQL.
        
        :param query: Truy vấn SQL
        :param params: Tham số của truy vấn
        :return: Kết quả của truy vấn, hoặc None nếu có lỗi xảy ra
        """
        if self.cursor:
            try:
                self.cursor.execute(query, params)
                return self.cursor.fetchall()
            except Exception as e:
                self._notify_error(f"Query failed: {e}")
                return None
        else:
            self._notify_error("Cursor is not initialized.")
            return None
        
    # Hàm đăng ký người dùng
    def register(self, username, password) -> bool:
        try:
            self.cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            self.conn.commit()
            return True
        except psycopg2.IntegrityError:
            self.conn.rollback()  # Hoàn tác giao dịch nếu có lỗi
            return False
    
    def login(self, username, password):
        self.cursor.execute("SELECT id FROM users WHERE username = %s AND password = %s", (username, password))
        result = self.cursor.fetchone()
        return result is not None
    
    def handle_message(self, sender, receiver, message) -> bool:
        # Kiểm tra nếu sender bị receiver block
        self.cursor.execute('''
            SELECT * FROM blocks
            WHERE user_id = (SELECT id FROM users WHERE username = %s)
            AND blocked_user_id = (SELECT id FROM users WHERE username = %s)
        ''', (receiver, sender))
        
        if self.cursor.fetchone():
            return False  # Sender bị block bởi receiver

        # Logic xử lý tin nhắn (lưu tin nhắn vào cơ sở dữ liệu hoặc gửi cho người nhận)
        # Ví dụ: self.cursor.execute("INSERT INTO messages (sender, receiver, message) VALUES (%s, %s, %s)", (sender, receiver, message))

        return True  # Tin nhắn đã được gửi thành công

    def handle_friend_request(self, sender, receiver) -> bool:
        self.cursor.execute("SELECT id FROM users WHERE username = %s", (receiver,))
        if self.cursor.fetchone():
            self.cursor.execute('''
                INSERT INTO friendships (user_id, friend_id, status)
                VALUES ((SELECT id FROM users WHERE username = %s), (SELECT id FROM users WHERE username = %s), 'pending')
            ''', (sender, receiver))
            self.conn.commit()
            return True  # Yêu cầu kết bạn đã được gửi
        else:
            return False  # Người nhận không tồn tại

    def handle_accept_friend(self, sender, friend) -> bool:
        self.cursor.execute('''
            UPDATE friendships SET status = 'accepted'
            WHERE user_id = (SELECT id FROM users WHERE username = %s)
            AND friend_id = (SELECT id FROM users WHERE username = %s)
            AND status = 'pending'
        ''', (friend, sender))
        self.conn.commit()

        # Kiểm tra nếu có bản ghi được cập nhật
        return self.cursor.rowcount > 0  # True nếu yêu cầu được chấp nhận, False nếu không tìm thấy yêu cầu pending


    def handle_block_user(self, blocker, blockee) -> bool:
        self.cursor.execute("SELECT id FROM users WHERE username = %s", (blockee,))
        if self.cursor.fetchone():
            self.cursor.execute('''
                INSERT INTO blocks (user_id, blocked_user_id)
                VALUES ((SELECT id FROM users WHERE username = %s), (SELECT id FROM users WHERE username = %s))
            ''', (blocker, blockee))
            self.conn.commit()
            return True  # Người dùng đã bị block thành công
        else:
            return False  # Người dùng không tồn tại

            

    def _notify(self, message):
        """
        Thông báo.
        """
        if self.message_callback:
            self.message_callback(f'Notify: {message}')

    def _notify_error(self, message):
        """
        Thông báo lỗi.
        """
        if self.message_callback:
            self.message_callback(f'Error: {message}')
    
    def create_all_tables(self):
        self.cur.execute("""
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            );
        """)
        self.cur.execute("""
            CREATE TABLE friendships (
                id SERIAL PRIMARY KEY,
                user_id INT REFERENCES users(id),
                friend_id INT REFERENCES users(id),
                status VARCHAR(20) CHECK (status IN ('pending', 'accepted', 'blocked'))
            );
        """)
        self.cur.execute("""
            CREATE TABLE blocks (
                id SERIAL PRIMARY KEY,
                user_id INT REFERENCES users(id),
                blocked_user_id INT REFERENCES users(id)
            );
        """)
        self.conn.commit()