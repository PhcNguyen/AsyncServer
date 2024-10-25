# Copyright (C) PhcNguyen Developers
# Distributed under the terms of the Modified BSD License.



def is_valid_user_id(user_id):
    try:
        return int(user_id)
    except ValueError:
        return None