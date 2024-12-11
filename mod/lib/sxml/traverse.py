from typing import Any, Callable
from mod.lib.sxml import SxmlNode

SxmlTraversalTag = Any
SxmlTraversalCallback = Callable[[SxmlNode|str, int, SxmlTraversalTag], SxmlTraversalTag|None]

def sxml_traverse(x: SxmlNode|str, indent: int, tag: SxmlTraversalTag, fn_start: SxmlTraversalCallback, fn_end: SxmlTraversalCallback):
    tag = fn_start(x, indent, tag)
    if not tag:
        return

    if type(x) is SxmlNode:
        for xx in x.xs:
            sxml_traverse(xx, indent + 1, tag, fn_start, fn_end)
    fn_end(x, indent, tag)