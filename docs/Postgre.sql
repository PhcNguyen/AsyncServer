CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE friendships (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    friend_id INT REFERENCES users(id),
    status VARCHAR(20) CHECK (status IN ('pending', 'accepted', 'blocked'))
);

CREATE TABLE blocks (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    blocked_user_id INT REFERENCES users(id)
);
