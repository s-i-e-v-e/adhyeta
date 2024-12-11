from mod.lib import is_not_empty, head
from mod.root.data.private import Database, Row, dataclass

@dataclass
class Word:
    id:  int
    word: str

@dataclass
class KnownWord:
    id:  int
    word: str
    is_known: bool
    ignore: bool
    note: str

def __build(xs: Row):
    return Word(*xs)

def __list(xss: list[Row]):
    return [__build(xs) for xs in xss]

def get_by_word(db: Database, w: str):
    return __build(head(db.exec("SELECT id, word FROM words WHERE word = ?", w)))

def get(db: Database, id: int):
    return __build(head(db.exec("SELECT id, word FROM words WHERE id = ?", id)))

def save(db: Database, w: str):
    db.exec("INSERT OR IGNORE INTO words(word) VALUES(?)", w)
    return __build(db.exec("SELECT id, word FROM words WHERE word = ?", w)[0])

def clear(db: Database):
    db.exec("DELETE FROM words")

def count_by_doc(db: Database, uuid: str):
    return int(db.exec("SELECT COUNT(doc_uuid) FROM doc_words WHERE doc_uuid = ?", uuid)[0][0])

def words(db: Database, uuid: str, user_id: int) -> list[KnownWord]:
    # get complete word map for user-document
    xs = db.exec("""
        SELECT w.id, w.word, kw.is_known, kw.ignore, kw.note FROM words w
        INNER JOIN doc_words dw ON dw.word_id = w.id AND dw.doc_uuid = ?
        LEFT OUTER JOIN known_words kw ON kw.word_id = dw.word_id AND kw.word_id = w.id AND kw.user_id = ?
        """, uuid, user_id)
    return [KnownWord(*r) for r in xs]

def words_by_doc(db: Database, uuid: str):
    return __list(db.exec("SELECT w.id, w.word FROM words w INNER JOIN doc_words dw on dw.word_id = w.id WHERE dw.doc_uuid = ?", uuid))

def words_by_doc_for_user(db: Database, uuid: str, user_id: int):
    return __list(db.exec("""
    SELECT w.id, w.word FROM words w
    INNER JOIN doc_words dw on dw.word_id = w.id
    INNER JOIN known_words kw on kw.word_id = w.id
    WHERE dw.doc_uuid = ? AND kw.user_id = ?
    """, uuid, user_id))

def word_status_toggle(db: Database, user_id: int, word_id: int):
    exists = is_not_empty(db.exec("SELECT id FROM known_words WHERE user_id = ? AND word_id = ?", user_id, word_id))
    if exists:
        db.exec("""
        UPDATE known_words SET is_known = iif(is_known = 1, 0, 1) WHERE user_id = ? AND word_id = ?
        """, user_id, word_id)
    else:
        db.exec("""
                INSERT INTO known_words(user_id, word_id, is_known, ignore, note) VALUES(?, ?, ?, ?, ?)
                """, user_id, word_id, True, False, "")
    return head(db.exec("SELECT is_known FROM known_words WHERE user_id = ? AND word_id = ?", user_id, word_id))[0]

# @dataclasses.dataclass
# class WordStats:
#     doc_id: int
#     doc_part_id: int
#     user_id: int
#     known_words: int
#     total_words: int
#
#
#

#
# def word_note_set(db: Database, user_id: int, word_id: int, note: str):
#     db.exec("UPDATE kw SET note = ? FROM known_word kw INNER JOIN word w ON w.id = kw.word_id INNER JOIN user u ON u.id = kw.user_id where u.id = ? AND w.id = ?",
#         note, user_id, word_id)
#
# def word_filter(db: Database, id: int, n: int):
#     return db.exec("SELECT id, word, is_known, note from word where ignore = 0 order by word LIMIT ? offset ?", n, id)
#
# def word_get_stats(db: Database, doc_id: int, user_id: int) -> list[WordStats]:
#     xs = db.exec("SELECT doc_part_id, COUNT(DISTINCT word_id) FROM vw_word vw WHERE doc_id = ? AND user_id = ? AND ignore = 0 AND is_known = 1 GROUP BY doc_part_id ORDER BY doc_part_id", doc_id, user_id)
#     ys = db.exec("SELECT doc_part_id, COUNT(DISTINCT word_id) FROM vw_word vw WHERE doc_id = ? AND user_id = ? AND ignore = 0 GROUP BY doc_part_id ORDER BY doc_part_id", doc_id, user_id)
#     zs = []
#     for xx, yy in zip(xs, ys):
#         if xx[0] != yy[0]:
#             raise Exception()
#         zs.append(WordStats(doc_id, xx[0], user_id, xx[1], yy[1]))
#     return zs
