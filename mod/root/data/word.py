from mod.lib.crypto import blake3_128
from mod.lib.text import devanagari_to_iso
from mod.root.data.private import Database, dataclass, __build, __list

@dataclass
class Word:
    hash:  bytes
    word: str
    word_o: str
    is_flagged: bool
    vy: str

@dataclass
class KnownWord:
    hash:  bytes
    word: str
    word_o: str
    is_flagged: bool
    is_known: bool
    ignore: bool
    note: str

def __devanagari_to_hash(w: str) -> bytes:
    return blake3_128(devanagari_to_iso(w))

def get(db: Database, w: str):
    hash = __devanagari_to_hash(w)
    return __build(Word, db.head("SELECT hash, word, word_o, is_flagged, vy FROM words WHERE hash = ?", hash))

def save(db: Database, w: str):
    wo = w
    w = devanagari_to_iso(w)
    hash = blake3_128(w)
    db.exec("INSERT OR IGNORE INTO words(hash, word, word_o, is_flagged, vy) VALUES(?, ?, ?, ?, ?)", hash, w, wo, False, "")
    return Word(hash, w, wo, False, "")

def count_by_doc(db: Database, uuid: str):
    return int(db.exec("SELECT COUNT(doc_uuid) FROM doc_words WHERE doc_uuid = ?", uuid)[0][0])

def count_by_user_and_doc(db: Database, uuid: str, user_id: int):
    return int(db.exec("SELECT COUNT(*) FROM known_words kw INNER JOIN doc_words dw ON dw.word_hash = kw.word_hash WHERE kw.is_known = 1 AND dw.doc_uuid = ? AND kw.user_id = ?", uuid, user_id)[0][0])

def get_note(db: Database, user_id: int, hash: bytes):
    return db.head("""SELECT note FROM known_words WHERE user_id = ? AND word_hash = ?""", user_id, hash)

def words_by_doc(db: Database, uuid: str) -> list[Word]:
    return __list(Word, db.exec("""
        SELECT hash, word, word_o, is_flagged, vy FROM words WHERE hash IN (SELECT word_hash FROM doc_words WHERE doc_uuid = ?)
        """, uuid))

def words_by_user(db: Database, uuid: str, user_id: int) -> list[KnownWord]:
    # get complete word map for user-document
    return __list(KnownWord, db.exec("""
        SELECT w.hash, w.word, w.word_o, w.is_flagged, kw.is_known, kw.ignore, kw.note FROM words w
        INNER JOIN doc_words dw ON dw.word_hash = w.hash AND dw.doc_uuid = ?
        LEFT OUTER JOIN known_words kw ON kw.word_hash = dw.word_hash AND kw.word_hash = w.hash AND kw.user_id = ?
        """, uuid, user_id))

def flag(db: Database, w: str):
    word_hash = __devanagari_to_hash(w)
    db.exec("UPDATE words SET is_flagged = iif(is_flagged = 1, 0, 1) WHERE hash = ?", word_hash)

def __make_known_word(db: Database, user_id: int, hash: bytes):
    db.exec("""INSERT INTO known_words(user_id, word_hash, is_known, ignore, note) VALUES(?, ?, ?, ?, ?) ON CONFLICT(user_id, word_hash) DO NOTHING""", user_id, hash, False, False, "")
    db.fhead("SELECT is_known FROM known_words WHERE user_id = ? and word_hash = ?", user_id, hash)

def note(db: Database, user_id: int, hash: bytes, note: str):
    __make_known_word(db, user_id, hash)
    db.exec("UPDATE known_words SET note = ? WHERE user_id = ? AND word_hash = ?", note, user_id, hash)

def known(db: Database, user_id: int, w: str):
    word_hash = __devanagari_to_hash(w)
    __make_known_word(db, user_id, word_hash)
    db.exec("""UPDATE known_words SET is_known = iif(is_known = 1, 0, 1) WHERE user_id = ? AND word_hash = ?""", user_id, word_hash)


def info(db: Database, user_id: int, w: str) -> tuple[bool, bool]:
    word_hash = __devanagari_to_hash(w)
    xs = db.head("SELECT is_known FROM known_words WHERE user_id = ? and word_hash = ?", user_id, word_hash)
    is_known = xs[0] == 1 if xs else False
    is_flagged = db.fhead("SELECT is_flagged FROM words WHERE hash = ?", word_hash)[0] == 1
    return is_known, is_flagged
