from mod.env import env
from mod.lib import fs
from mod.lib.sqlite_db import Database
from mod.root.data import word as word

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
CREATE TABLE IF NOT EXISTS doc_word(
    id INTEGER PRIMARY KEY,
    doc_id INTEGER NOT NULL,
    word_id INTEGER NOT NULL,
    FOREIGN KEY(doc_id) REFERENCES docs(id),
    FOREIGN KEY(word_id) REFERENCES words(id),
    UNIQUE(doc_id, word_id)
    );
"""

]

name = f"{env.DATA_ROOT}/adhyeta.sqlite3"
exists = fs.exists(name)
repo = Database(name, sql)

def init():
    from mod.root.data import user
    if not exists:
        u, e, p = env.ROOT_USER.split(":")
        user.add(repo, u, e, p)

init()