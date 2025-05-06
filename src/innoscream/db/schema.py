CREATE_POSTS = """
CREATE TABLE IF NOT EXISTS posts (
    post_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    user_hash   TEXT    NOT NULL,
    text        TEXT    NOT NULL,
    skull       INTEGER NOT NULL DEFAULT 0,
    fire        INTEGER NOT NULL DEFAULT 0,
    clown       INTEGER NOT NULL DEFAULT 0,
    message_id  INTEGER NOT NULL,
    chat_id     INTEGER NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted  INTEGER NOT NULL DEFAULT 0
);
"""

CREATE_STATS = """
CREATE TABLE IF NOT EXISTS user_stats (
    user_hash  TEXT PRIMARY KEY,
    post_count INTEGER NOT NULL DEFAULT 0
);
"""

CREATE_REACTIONS = """
CREATE TABLE IF NOT EXISTS reactions (
    post_id     INTEGER NOT NULL,
    user_hash   TEXT    NOT NULL,
    emoji       TEXT    NOT NULL,
    PRIMARY KEY (post_id, user_hash)
);
"""

SCHEMA_DDL = CREATE_POSTS + CREATE_STATS + CREATE_REACTIONS
