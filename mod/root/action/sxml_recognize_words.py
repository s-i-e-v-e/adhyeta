from mod.lib import sxml, head
from mod.lib.text import to_sa_words
from mod.root.data import word, db, dataclass

@dataclass
class Tag:
    parent: sxml.SxmlNode
    words: list[word.KnownWord]

DOC_TEXT_ELEMENTS = ["p", "corr", "title", "\"", "'", "q"]

def __start(x: sxml.SxmlNode|str, index: int, indent: int, q: Tag):
    if type(x) is str:
        if q.parent.path.startswith("/document") and q.parent.id in DOC_TEXT_ELEMENTS:
            q.parent.xs.pop(index)
            i = 0
            for y, w in to_sa_words(x):
                if y:
                    ww = head([x for x in q.words if x.word == w])
                    n = sxml.SxmlNode(f"{q.parent.path}/w", q.parent.line, "w", {}, [w])
                    if ww:
                        n.attrs["id"] = f"w{ww.id}"
                        if ww.is_known:
                            n.attrs["is-k"] = ""
                    q.parent.xs.insert(index + i, n)
                else:
                    q.parent.xs.insert(index + i, w)
                i += 1
        return None
    elif type(x) is sxml.SxmlNode:
        return Tag(x, q.words)
    else:
        raise TypeError(x)

def __end(x: sxml.SxmlNode|str, index: int, indent: int, q: Tag):
    return None

def recognize_words(n: sxml.SxmlNode, user_id: int):
    q = Tag(n, word.words(db, n.attrs["uuid"], user_id))
    sxml.traverse(n, q, __start, __end)