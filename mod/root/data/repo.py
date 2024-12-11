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
    ) STRICT;
""",
"""
CREATE TABLE IF NOT EXISTS docs(
    id INTEGER PRIMARY KEY,
    uuid TEXT UNIQUE NOT NULL,
    loc TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    text TEXT NOT NULL,
    metadata TEXT NOT NULL,
    update_timestamp_ns INTEGER NOT NULL
    ) STRICT;
""",
"""
CREATE TABLE IF NOT EXISTS words(
    hash BLOB(16) PRIMARY KEY, /* blake3_128 */
    word TEXT UNIQUE NOT NULL, /* stored as iso-15919 */
    word_o TEXT NOT NULL, /* caching original word for fast comparison */
    is_flagged BOOLEAN NOT NULL,
    vy TEXT NOT NULL
    ) WITHOUT ROWID;
""",
"""
CREATE TABLE IF NOT EXISTS doc_words(
    doc_uuid TEXT NOT NULL,
    word_hash BLOB(16) NOT NULL,
    FOREIGN KEY(doc_uuid) REFERENCES docs(uuid),
    FOREIGN KEY(word_hash) REFERENCES words(hash),
    PRIMARY KEY(doc_uuid, word_hash)
    ) WITHOUT ROWID;
""",
"""
CREATE TABLE IF NOT EXISTS known_words(
    word_hash BLOB(16) NOT NULL,
    user_id INTEGER NOT NULL,
    is_known INTEGER NOT NULL,
    ignore INTEGER NOT NULL,
    note TEXT,
    FOREIGN KEY(word_hash) REFERENCES words(hash),
    FOREIGN KEY(user_id) REFERENCES users(id),
    PRIMARY KEY(word_hash, user_id)
    ) WITHOUT ROWID;
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