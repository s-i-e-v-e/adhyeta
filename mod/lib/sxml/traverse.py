from typing import Any, Callable
from mod.lib.sxml import SxmlNode

SxmlTraversalTag = Any
SxmlTraversalCallback = Callable[[SxmlNode|str, int, int, SxmlTraversalTag], SxmlTraversalTag|None]

def sxml_traverse(x: SxmlNode|str, tag: SxmlTraversalTag, fn_start: SxmlTraversalCallback, fn_end: SxmlTraversalCallback):
    __sxml_traverse(x, -1, 0, tag, fn_start, fn_end)

def __sxml_traverse(x: SxmlNode|str, index: int, indent: int, tag: SxmlTraversalTag, fn_start: SxmlTraversalCallback, fn_end: SxmlTraversalCallback):
    tag = fn_start(x, index, indent, tag)
    if not tag:
        return

    if type(x) is SxmlNode:
        i = 0
        for xx in x.xs:
            __sxml_traverse(xx, i, indent + 1, tag, fn_start, fn_end)
            i += 1
    fn_end(x, index, indent, tag)