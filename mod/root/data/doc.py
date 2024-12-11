from mod.lib.text import from_json
from mod.root.data.private import Database, Row, dataclass, __list, __build, __fbuild

@dataclass
class DocMetadata:
    title: str
    copyright: str
    author: str
    category: str
    note: str
    unique_words: int
    total_words: int
    source: str
    source_page: str
    source_url: str
    source_date: str
    original_loc: str

@dataclass
class Doc:
    id:  int
    uuid: str
    loc: str
    title: str
    text: str
    metadata: str
    update_timestamp_ns: int

def meta_to_metadata(x: str):
    y = from_json(x)
    def k(a: str):
        return y.get(a, '')

    return DocMetadata(
        k('title'),
        k('copyright'),
        k('author'),
        k('category'),
        k('note'),
        int(k('unique_words')),
        int(k('total_words')),
        k('source'),
        k('source_page'),
        k('source_url'),
        k('source_date'),
        k('original_loc')
    )

VirtualFS = dict[str, list[str]]

def vfs(db: Database) -> VirtualFS:
    q = VirtualFS()

    def add_to_parent(loc: str):
        def add(p: str, c: str):
            if p != c:
                q[p].append(c)

        xs = loc.split("/")
        ys = []
        pp = ""
        for x in xs:
            ys.append(x)
            yy = "/".join(ys)
            if yy not in q:
                q[yy] = []
            add(pp, yy)
            pp = yy

        ys = xs[0:-1]
        yy = "/".join(ys)
        add(yy, loc)

    for d in all(db):
        add_to_parent(d.loc)

    for k in q.keys():
        xs = list(set(q[k]))

        for f in xs:
            if f.endswith("/index.sxml"):
                xs.remove(f)
                xs.insert(0, f)
                break
        q[k] = xs
    return q

def all(db: Database):
    return __list(Doc, db.exec("SELECT id, uuid, loc, title, '', metadata, update_timestamp_ns FROM docs ORDER BY loc ASC"))

def get_child_docs(db: Database, parent_loc: str):
    return __list(Doc, db.exec("SELECT id, uuid, loc, title, '', metadata, update_timestamp_ns FROM docs WHERE loc LIKE ? ORDER BY loc ASC", f"{parent_loc}/%"))

def get_by_loc(db: Database, loc: str):
    return __build(Doc, db.head("SELECT id, uuid, loc, title, text, metadata, update_timestamp_ns FROM docs WHERE loc = ?", loc))

def get_by_uuid(db: Database, uuid: str):
    return __build(Doc, db.head("SELECT id, uuid, loc, title, text, metadata, update_timestamp_ns FROM docs WHERE uuid = ?", uuid))

def save(db: Database, uuid: str, loc: str, title: str, text: str, metadata: str, update_timestamp_ns: int, words: list[tuple[bytes, str, str]]):
    db.exec("DELETE FROM doc_words WHERE doc_uuid = ?", uuid)

    db.exec("DELETE FROM docs WHERE uuid = ?", uuid)
    db.exec("INSERT OR IGNORE INTO docs(uuid, loc, title, text, metadata, update_timestamp_ns) VALUES(?, ?, ?, ?, ?, ?)", uuid, loc, title, text, metadata, update_timestamp_ns)
    d = __build(Doc, db.head("SELECT id, uuid, loc, title, text, metadata, update_timestamp_ns FROM docs WHERE loc = ?", loc))

    qw = None
    try:
        for w in words:
            qw = w
            b, q, z = qw
            db.exec("INSERT INTO doc_words(doc_uuid, word_hash) VALUES(?, ?)", uuid, b)
        return d
    except Exception as e:
        print(f"INSERT: {loc} {uuid}")


        print('===============PREV=================')
        for w in words:
            hash, word, word_o = w
            if hash == qw[0]:
                debug_word(word, word_o)
                print(w)
                print(f'{hash.hex()} - {word} - {word.encode('utf-8').hex()} - {word_o} - {word_o.encode('utf-8').hex()}')
        raise e

def debug_word(word: str, word_o: str):
    for x in word_o:
        print(f'{x} - {hex(ord(x))}')