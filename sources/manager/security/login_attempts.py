# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.

import datetime


class LoginAttempts:
    MAX_ATTEMPTS = 5
    LOCKOUT_TIME = 300  # 5 phút

    def __init__(self):
        self.attempts = {}
        self.locked_accounts = {}

    def is_account_locked(self, username):
        if username in self.locked_accounts:
            lock_time = self.locked_accounts[username]
            if (datetime.datetime.utcnow() - lock_time).total_seconds() < self.LOCKOUT_TIME:
                return True
            else:
                del self.locked_accounts[username]
        return False

    def record_failed_attempt(self, username):
        if username not in self.attempts:
            self.attempts[username] = 0
        self.attempts[username] += 1

        if self.attempts[username] >= self.MAX_ATTEMPTS:
            self.locked_accounts[username] = datetime.datetime.utcnow()

    def reset_attempts(self, username):
        if username in self.attempts:
            del self.attempts[username]