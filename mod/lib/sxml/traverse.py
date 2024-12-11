from typing import Any, Callable
from mod.lib.sxml import SxmlNode

ChildNodes = list[SxmlNode|str]
SxmlTraversalTag = Any
SxmlTraversalCallback = Callable[[ChildNodes, int, int, SxmlTraversalTag], SxmlTraversalTag]

def sxml_traverse(x: SxmlNode, tag: SxmlTraversalTag, fn_start: SxmlTraversalCallback, fn_end: SxmlTraversalCallback|None = None):
    __sxml_traverse([x], 0, tag, fn_start, fn_end)

def __sxml_traverse(xs: ChildNodes, indent: int, tag: SxmlTraversalTag, fn_start: SxmlTraversalCallback, fn_end: SxmlTraversalCallback|None = None):
    for i, _ in enumerate(xs):
        tag_x = tag
        tag_x = fn_start(xs, i, indent, tag_x)
        if not tag_x:
            continue
        x = xs[i]
        if type(x) is SxmlNode:
            __sxml_traverse(x.xs, indent + 1, tag_x, fn_start, fn_end)
        if fn_end:
            fn_end(xs, i, indent, tag_x)
