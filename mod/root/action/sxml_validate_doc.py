from dataclasses import dataclass
from mod.lib import sxml

VALID_ELEMENTS = ["document", "copyright", "source", "title", "author", "category", "note", "sec", "corr", "sic", "x-list", "\"", "\'", "q", "v", "a", "p", "ul", "li", "lit", "em", "img"]
@dataclass
class Tag:
    ss: set[str]

def __start(x: sxml.SxmlNode|str, index: int, indent: int, q: Tag):
    if type(x) is str:
        return None
    elif type(x) is sxml.SxmlNode:
        if x.id not in VALID_ELEMENTS:
            raise Exception(f"invalid element {x.id}")
        else:
            return Tag(q.ss)
    else:
        raise TypeError(x)

def __end(x: sxml.SxmlNode|str, index: int, indent: int, q: Tag):
    return None

def validate(n: sxml.SxmlNode):
    q = Tag(set())
    sxml.traverse(n, q, __start, __end)
    return q.ss
