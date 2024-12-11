from mod.root.data.private import Database, Row, dataclass

@dataclass
class Doc:
    id:  int
    uuid: str
    loc: str
    title: str
    text: str
    update_timestamp_ns: int

def __build(xs: Row):
    return Doc(*xs)

def head(xss: list[Row]) -> Doc|None:
    return __build(xss[0]) if len(xss) else None

def all(db: Database):
    return [__build(xs) for xs in db.exec("SELECT id, uuid, loc, title, '', update_timestamp_ns FROM docs ORDER BY loc ASC")]

def get_child_docs(db: Database, parent_loc: str):
    return [__build(xs) for xs in db.exec("SELECT id, uuid, loc, title, '', update_timestamp_ns FROM docs WHERE loc LIKE ? ORDER BY loc ASC", f"{parent_loc}/%")]

def get_by_loc(db: Database, loc: str):
    return head(db.exec("SELECT id, uuid, loc, title, text, update_timestamp_ns FROM docs WHERE loc = ?", loc))

def get_by_uuid(db: Database, uuid: str):
    return head(db.exec("SELECT id, uuid, loc, title, text, update_timestamp_ns FROM docs WHERE uuid = ?", uuid))

def get(db: Database, id: int):
    return head(db.exec("SELECT id, uuid, loc, title, text, update_timestamp_ns FROM docs WHERE id = ?", id))

def save(db: Database, uuid: str, loc: str, title: str, text: str, update_timestamp_ns: int, words: list[int]):
    db.exec("DELETE FROM doc_words WHERE doc_uuid = ?", uuid)

    db.exec("DELETE FROM docs WHERE uuid = ?", uuid)
    db.exec("INSERT OR IGNORE INTO docs(uuid, loc, title, text, update_timestamp_ns) VALUES(?, ?, ?, ?, ?)", uuid, loc, title, text, update_timestamp_ns)
    d = head(db.exec("SELECT id, uuid, loc, title, text, update_timestamp_ns FROM docs WHERE loc = ?", loc))

    for w in words:
        db.exec("INSERT INTO doc_words(doc_uuid, word_id) VALUES(?, ?)", uuid, w)
    return d
