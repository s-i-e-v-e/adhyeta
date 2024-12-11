from dataclasses import dataclass

from mod.root.data import Database

@dataclass
class Doc:
    id:  int
    loc: str
    title: str
    text: str
    update_timestamp_ns: int

def __build(*args, **kwargs):
    return Doc(*args, **kwargs)

def list(db: Database):
    return [__build(*xs) for xs in db.exec("SELECT id, loc, title, '', update_timestamp_ns FROM docs ORDER BY loc ASC")]

def get_child_docs(db: Database, parent_loc: str):
    return [__build(*xs) for xs in db.exec("SELECT id, loc, title, '', update_timestamp_ns FROM docs WHERE loc LIKE ? ORDER BY loc ASC", f"{parent_loc}/%")]

def get_by_loc(db: Database, loc: str) -> Doc:
    return __build(*db.exec("SELECT id, loc, title, text, update_timestamp_ns FROM docs WHERE loc = ?", loc)[0])

def get(db: Database, id: int):
    return __build(*db.exec("SELECT id, loc, title, text, update_timestamp_ns FROM docs WHERE id = ?", id)[0])

def save(db: Database, loc: str, title: str, text: str, update_timestamp_ns: int):
    db.exec("DELETE FROM docs WHERE loc = ?", loc)
    db.exec("INSERT OR IGNORE INTO docs(loc, title, text, update_timestamp_ns) VALUES(?, ?, ?, ?)", loc, title, text, update_timestamp_ns)
    return __build(*db.exec("SELECT id, loc, title, text, update_timestamp_ns FROM docs WHERE loc = ?", loc)[0])