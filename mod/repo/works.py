import tempfile

from mod.repo.db import Database
from mod.tools.qp import do_import
from mod.util.fs import read_text, list_dirs, read_json, list_files
import re

def works_import_all():
    with tempfile.TemporaryDirectory() as dp:
        do_import(dp)
        for f in list_dirs(dp):
            works_import(f"{dp}/{f}")

def works_import(path: str):
    meta = read_json(f'{path}/meta.json')

    db = Database()
    db.begin()
    exists = db.exec("SELECT COUNT(id) FROM work WHERE name = ?", meta['name'])[0][0] == 1
    if not exists:
        for [id] in db.exec("INSERT INTO work(name) VALUES(?) RETURNING id", meta['name']):
            __import_parts(db, path, id)
    db.commit()


def __import_parts(db: Database, path: str, id: int):
    for f in list_files(path):
        if not f.endswith('.txt'):
            continue
        x = read_text(f'{path}/{f}')
        xs = x.split('\n')

        part_id = db.exec("INSERT INTO part(work_id, name) VALUES(?, ?) RETURNING id", id, xs[0])[0][0]
        __import_lines(db, part_id, xs)


num_re = re.compile(r'॥\d+.*')
delimiters = ["(", ")", "?", "!", ".", ",", "।", "॥", " ", "-", "/"]
splitter = '|'.join(map(re.escape, delimiters))
def __import_lines(db: Database, part_id: int, xs):
    line = 1
    for x in xs:
        word = 1
        for y in re.split(f"({splitter})", x):
            ignore = y in delimiters
            db.exec("INSERT OR IGNORE INTO word(word, is_known, ignore) VALUES(?, ?, ?)", y, 0, ignore)
            db.exec("INSERT INTO part_word(part_id, word_id, line_no, word_no) VALUES(?, (SELECT id FROM word WHERE word = ?), ?, ?)", part_id, y, line, word)
            word += 1
        line += 1

def works_list_all():
    db = Database()
    return db.exec("SELECT id, name FROM work")

def work_load(work_id: int):
    db = Database()
    xs = list(db.exec("SELECT id, name FROM work WHERE id = ?", work_id))
    return xs[0]

def parts_list_all(work_id: int):
    db = Database()
    return list(db.exec("SELECT id, name FROM part WHERE work_id = ?", work_id))

def part_load(part_id: int):
    db = Database()
    return list(db.exec("SELECT word_id, word, is_known, ignore, line_no, word_no, note FROM part_word pw INNER JOIN word w on w.id = pw.word_id WHERE part_id = ? ORDER BY line_no, word_no", part_id))

def word_status_toggle(id: int):
    db = Database()
    db.exec("UPDATE word SET is_known = iif(is_known = 1, 0, 1) where id = ?", id)

def word_note_set(id: int, note: str):
    db = Database()
    db.exec("UPDATE word SET note = ? where id = ?", note, id)

def word_get(id: int):
    db = Database()
    return db.exec("SELECT id, word, is_known, ignore, note FROM word WHERE id = ?", id)[0]

def word_filter(id: int, n: int):
    db = Database()
    return db.exec("SELECT id, word, is_known, note from word where ignore = 0 order by word LIMIT ? offset ?", n, id)
