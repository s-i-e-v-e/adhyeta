from mod.env import env
from mod.lib import fs
from mod.lib.sqlite_db import Database

sql = [
"""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY,
    user TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    hash TEXT NOT NULL
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

init()