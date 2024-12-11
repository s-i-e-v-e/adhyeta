import pickle

from mod.lib.sqlite_db import Database
from mod.lib.sxml.parser import SxmlNode

def db_init():
    sql = [
        """
        CREATE TABLE book(id INTEGER PRIMARY KEY, loc TEXT UNIQUE NOT NULL, title TEXT, content BLOB, content_text TEXT, skip BOOL);
        """
    ]
    global db
    return Database(":memory:", sql)

def db_insert(db: Database, loc: str, title: str, n: SxmlNode, text: str, skip: bool):
    db.exec("INSERT INTO book(loc, title, content, content_text, skip) VALUES (?, ?, ?, ?, ?)", loc, title, pickle.dumps(n), text, skip)

def db_list_locations(db: Database):
    return list(db.exec("SELECT loc FROM book order by loc ASC"))

def db_select(db: Database, loc: str):
    xs = list(db.exec("SELECT title, content, content_text, skip FROM book WHERE loc = ?", loc))
    return [(title, pickle.loads(content), text, skip) for (title, content, text, skip) in xs]