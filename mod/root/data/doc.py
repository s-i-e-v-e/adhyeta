from mod.root.data.private import Database, Row, dataclass, __list, __build, __fbuild


@dataclass
class Doc:
    id:  int
    uuid: str
    loc: str
    title: str
    text: str
    update_timestamp_ns: int

def all(db: Database):
    return __list(Doc, db.exec("SELECT id, uuid, loc, title, '', update_timestamp_ns FROM docs ORDER BY loc ASC"))

def get_child_docs(db: Database, parent_loc: str):
    return __list(Doc, db.exec("SELECT id, uuid, loc, title, '', update_timestamp_ns FROM docs WHERE loc LIKE ? ORDER BY loc ASC", f"{parent_loc}/%"))

def get_by_loc(db: Database, loc: str):
    return __build(Doc, db.head("SELECT id, uuid, loc, title, text, update_timestamp_ns FROM docs WHERE loc = ?", loc))

def get_by_uuid(db: Database, uuid: str):
    return __build(Doc, db.head("SELECT id, uuid, loc, title, text, update_timestamp_ns FROM docs WHERE uuid = ?", uuid))

def save(db: Database, uuid: str, loc: str, title: str, text: str, update_timestamp_ns: int, words: list[bytes]):
    db.exec("DELETE FROM doc_words WHERE doc_uuid = ?", uuid)

    db.exec("DELETE FROM docs WHERE uuid = ?", uuid)
    db.exec("INSERT OR IGNORE INTO docs(uuid, loc, title, text, update_timestamp_ns) VALUES(?, ?, ?, ?, ?)", uuid, loc, title, text, update_timestamp_ns)
    d = __build(Doc, db.head("SELECT id, uuid, loc, title, text, update_timestamp_ns FROM docs WHERE loc = ?", loc))

    for w in words:
        db.exec("INSERT INTO doc_words(doc_uuid, word_hash) VALUES(?, ?)", uuid, w)
    return d
