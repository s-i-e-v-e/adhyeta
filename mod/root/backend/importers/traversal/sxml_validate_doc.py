from dataclasses import dataclass
from mod.lib import sxml
from mod.lib.sxml.traverse import ChildNodes
from mod.root.backend.importers import sxml_el

@dataclass
class Tag:
    ss: set[str]

def __start(xs: ChildNodes, index: int, indent: int, q: Tag):
    x = xs[index]
    if type(x) is str:
        return None
    elif type(x) is sxml.SxmlNode:
        if x.id not in sxml_el.VALID_DOC_ELEMENTS:
            raise Exception(f"invalid element {x.id}")
        else:
            return Tag(q.ss)
    else:
        raise TypeError(x)

def validate(n: sxml.SxmlNode):
    q = Tag(set())
    sxml.traverse(n, q, __start)
    return q.ss
