from dataclasses import dataclass
from mod.lib import sxml
from mod.lib.sxml.traverse import ChildNodes
from mod.lib.text import to_sa_words


@dataclass
class Tag:
    ss: set[str]
    total: int

def __start(xs: ChildNodes, index: int, indent: int, q: Tag):
    x = xs[index]
    if type(x) is str:
        for y, w in to_sa_words(x):
            if y:
                q.ss.add(w)
                q.total += 1
        return None
    elif type(x) is sxml.SxmlNode:
        if x.id in ["sic", "author", "source", "copyright", "meta", "title"]:
            return None
        else:
            return q
    else:
        raise TypeError(x)

def count_words(n: sxml.SxmlNode) -> tuple[set, int]:
    q = Tag(set(), 0)
    sxml.traverse(n, q, __start)
    return q.ss, q.total
