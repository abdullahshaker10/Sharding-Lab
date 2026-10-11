CREATE TABLE users (
    id         BIGINT PRIMARY KEY,
    name       TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE accounts (
    user_id BIGINT PRIMARY KEY,
    balance BIGINT NOT NULL CHECK (balance >= 0)
);

CREATE TABLE posts (
    id         BIGINT PRIMARY KEY,
    user_id    BIGINT NOT NULL,
    likes      INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX posts_user_id ON posts (user_id);
