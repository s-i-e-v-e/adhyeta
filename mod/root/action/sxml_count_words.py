from dataclasses import dataclass
from mod.lib import sxml
from mod.lib.text import to_sa_words


@dataclass
class Tag:
    ss: set[str]

def __start(x: sxml.SxmlNode|str, index: int, indent: int, q: Tag):
    if type(x) is str:
        for y, w in to_sa_words(x):
            if y:
                q.ss.add(w)
        return None
    elif type(x) is sxml.SxmlNode:
        if x.id in ["sic", "author", "source", "copyright", "meta"]:
            return Tag(set())
        else:
            return Tag(q.ss)
    else:
        raise TypeError(x)

def __end(x: sxml.SxmlNode|str, index: int, indent: int, q: Tag):
    return None

def count_words(n: sxml.SxmlNode):
    q = Tag(set())
    sxml.traverse(n, q, __start, __end)
    return q.ss
