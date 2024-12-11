from mod.config import env
from mod.lib import fs
from mod.root.data.private import Database

sql = [
"""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY,
    user TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    hash TEXT NOT NULL
    );
""",
"""
CREATE TABLE IF NOT EXISTS docs(
    id INTEGER PRIMARY KEY,
    uuid TEXT UNIQUE NOT NULL,
    loc TEXT UNIQUE NOT NULL,
    title TEXT,
    text TEXT,
    update_timestamp_ns INTEGER NOT NULL
    );
""",
"""
CREATE TABLE IF NOT EXISTS words(
    id INTEGER PRIMARY KEY,
    word TEXT UNIQUE NOT NULL
    );
""",
"""
CREATE TABLE IF NOT EXISTS doc_words(
    id INTEGER PRIMARY KEY,
    doc_uuid TEXT NOT NULL,
    word_id INTEGER NOT NULL,
    FOREIGN KEY(doc_uuid) REFERENCES docs(uuid),
    FOREIGN KEY(word_id) REFERENCES words(id),
    UNIQUE(doc_uuid, word_id)
    );
""",
"""
CREATE TABLE IF NOT EXISTS known_words(
    id INTEGER PRIMARY KEY,
    word_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    is_known BOOLEAN NOT NULL,
    ignore BOOLEAN NOT NULL,
    note TEXT,
    FOREIGN KEY(word_id) REFERENCES words(id),
    FOREIGN KEY(user_id) REFERENCES users(id)
    );
""",
]

name = f"{env.DATA_ROOT}/adhyeta.sqlite3"
exists = fs.exists(name)
repo = Database(name, sql)

def init():
    from mod.root.data import user
    if not exists:
        u, e, p = env.ROOT_USER.split(":")
        user.add(repo, u, e, p)