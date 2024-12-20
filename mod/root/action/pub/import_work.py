import time
from dataclasses import dataclass

from mod.lib import sxml
from mod.lib.fs import list_dirs, list_files, File, read_text
from mod.lib.text import is_devanagari, normalize, make_slug, to_sa_words
from mod.root.action.pub import State, get_document_title
from mod.root.data import word, doc

@dataclass
class WordCount:
    ss: set[str]

words_d = set()
words_nd = set()
def check_word(x: str):
    y, w = is_devanagari(x)
    if y:
        words_d.add(x)
    else:
        words_nd.add(f"{x} //{w}//")

def write_words():
    # xs = list(sorted(words))
    # xs.sort()
    # write_text(f"{dd}/word.list", "\n".join(xs))

    # write_text(f"{env.WWW_ROOT}/d.list", "\n".join(words_d))
    # write_text(f"{env.WWW_ROOT}/nd.list", "\n".join(words_nd))
    pass

def word_count_start(x: sxml.SxmlNode|str, indent: int, q: WordCount):
    if type(x) is str:
        # check_word(x)

        for y, w in to_sa_words(x):
            if y:
                q.ss.add(w)
        return None
    elif type(x) is sxml.SxmlNode:
        if x.id in ["sic", "author", "source", "copyright", "meta"]:
            return WordCount(set())
        else:
            return WordCount(q.ss)
    else:
        raise TypeError(x)

def word_count_end(x: sxml.SxmlNode|str, indent: int, q: WordCount):
    return None

def __import_file_into_db(state: State, f: File):
    if not f.name.endswith(".sxml"):
        raise Exception(f"Expected an SXML file. Found {f.full_path}")
    sf = f.full_path

    text = normalize(read_text(sf)).replace("--", "—").replace("-\n", "")
    n = sxml.parse(text)

    title = get_document_title(n)
    uuid = n.attrs["uuid"]
    loc = n.attrs["loc"]

    d =  doc.get_by_uuid(state.db, uuid)

    if loc.endswith(".sxml"):
        pass
    else:
        fn = "index.sxml" if f.name == "index.sxml" else f"{make_slug(title)}.sxml"
        loc = f"{loc}/{fn}"
        loc = loc.replace("//", "/")

    # count words
    q = WordCount(set())
    sxml.traverse(n, 0, q, word_count_start, word_count_end)
    ys = []
    for x in q.ss:
        w = word.save(state.db, x)
        ys.append(w.id)

    if d is None:
        print(f"Adding {loc}")
        d = doc.save(state.db, uuid, loc, title, text, time.time_ns(), ys)
    else:
        if d.text != text:
            print(f"Updating {loc}")
            d = doc.save(state.db, uuid, loc, title, text, time.time_ns(), ys)
    assert d


def import_files_into_db(state: State, p: File):
    for f in list_dirs(p.full_path):
        import_files_into_db(state, f)

    for f in list_files(p.full_path):
        __import_file_into_db(state, f)