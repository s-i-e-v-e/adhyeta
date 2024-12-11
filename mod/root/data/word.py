from dataclasses import dataclass

from mod.root.data import Database

@dataclass
class Word:
    id:  int
    word: str

def __build(*args, **kwargs):
    return Word(*args, **kwargs)

def get(db: Database, id: int):
    return __build(*db.exec("SELECT id, word FROM words WHERE id = ?", id)[0])

def save(db: Database, w: str):
    db.exec("INSERT OR IGNORE INTO words(word) VALUES(?)", w)
    return __build(*db.exec("SELECT id FROM words WHERE word = ?", w)[0])