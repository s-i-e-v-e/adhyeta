from mod.root.data.private import Database, Row, dataclass

@dataclass
class Word:
    id:  int
    word: str

def __build(xs: Row):
    return Word(*xs)

def head(xss: list[Row]) -> Word|None:
    return __build(xss[0]) if len(xss) else None

def get_by_word(db: Database, w: str):
    return head(db.exec("SELECT id, word FROM words WHERE word = ?", w))

def get(db: Database, id: int):
    return __build(db.exec("SELECT id, word FROM words WHERE id = ?", id)[0])

def save(db: Database, w: str):
    db.exec("INSERT OR IGNORE INTO words(word) VALUES(?)", w)
    return __build(db.exec("SELECT id, word FROM words WHERE word = ?", w)[0])

def clear(db: Database):
    db.exec("DELETE FROM words")