import typing

from mod.lib import text
from mod.lib.sxml import SxmlNode
from mod.lib.sxml.parser import parse
import re

OptionalSxmlNode = SxmlNode | None
SxmlNodePair = tuple[OptionalSxmlNode, OptionalSxmlNode]


def _filter_node(px: OptionalSxmlNode, cx: SxmlNode, i: int, qs: list[str]) -> SxmlNodePair:
    if qs[i] in cx.id:
        if i < len(qs) - 1:
            for y in cx.xs:
                if type(y) is SxmlNode:
                    zpx, zcx = _filter_node(cx, y, i + 1, qs)
                    if zcx:
                        return zpx, zcx
        else:
            return px, cx
    return px, None


def sxml_filter_node(x: SxmlNode, q: str) -> SxmlNodePair:
    q = q[1:]
    p, y = _filter_node(None, x, 0, q.split("/"))
    return p, y


def sxml_node_exists(x: SxmlNode, q: str) -> bool:
    p, y = sxml_filter_node(x, q)
    if not p or not y:
        return False
    return True


def sxml_remove_node(x: SxmlNode, q: str):
    p, y = sxml_filter_node(x, q)
    if not p or not y:
        return
    p.xs.remove(y)
    return y


def sxml_move_node_to(x: SxmlNode, q: str, index: int):
    y = sxml_remove_node(x, q)
    if not y:
        return
    x.xs.insert(index, y)


def sxml_move_node_to_end(x: SxmlNode, q: str):
    y = sxml_remove_node(x, q)
    if not y:
        return
    x.xs.append(y)


def _update_path(z: SxmlNode, q: str):
    z.path = "/".join(q.split("/")[:-1]) + "/" + z.id


def sxml_replace_node(x: SxmlNode, q: str, z: SxmlNode):
    p, y = sxml_filter_node(x, q)
    if not p or not y:
        return
    i = p.xs.index(y)
    p.xs[i] = z
    _update_path(z, q)


def sxml_insert_node(x: SxmlNode, q: str, z: SxmlNode, offset: int):
    p, y = sxml_filter_node(x, q)
    if not p or not y:
        return
    i = p.xs.index(y)
    j = max(i + offset, 0)
    p.xs.insert(j, z)
    _update_path(z, q)


def sxml_index_of(x: SxmlNode, q: str):
    p, y = sxml_filter_node(x, q)
    if not p or not y:
        return - 1
    return p.xs.index(y)

def sxml_get_str_node_val(x: SxmlNode, q: str) -> str:
    _, y = sxml_filter_node(x, q)
    if not y:
        return ""
    for a in y.xs:
        if type(a) is not str:
            raise Exception(f"Bad Node {q} [{type(a).__name__}]")

    xs = typing.cast(list[str], y.xs)
    return " ".join(xs).strip()


def sxml_node_as_str(x: SxmlNode, q: str) -> str:
    _, y = sxml_filter_node(x, q)
    if not y:
        return ""
    return __sxml_node_as_str(y, [])

def __sxml_node_as_str(x: SxmlNode, xs: list[str]) -> str:
    for a in x.xs:
        if type(a) is str:
            xs.append(a)
        else:
            a = typing.cast(SxmlNode, a)
            __sxml_node_as_str(a, xs)

    return re.sub(r"\s+", " ", " ".join(xs)).strip()


def sxml_is_action(x: SxmlNode) -> bool:
    return x.id.startswith("x-")

def sxml_is_sym(x: SxmlNode) -> bool:
    return re.match(r"[^a-zA-Z0-9][^-a-zA-Z0-9]*", x.id) is not None

def as_str(n: typing.Any) -> str:
    assert n and type(n) == str
    return n

def as_node(n: typing.Any) -> SxmlNode:
    assert n and type(n) == SxmlNode
    return n

def are_equal(a: SxmlNode, b: SxmlNode) -> bool:
    if a.id != b.id:
        print("ID MISMATCH")
        return False
    if len(a.attrs) != len(b.attrs):
        print("ATTRS MISMATCH")
        return False
    if sorted(a.attrs.keys()) != sorted(b.attrs.keys()):
        print("ATTRS MISMATCH #2")
        return False
    for k in a.attrs:
        if a.attrs[k] != b.attrs[k]:
            print("ATTRS MISMATCH #3")
            return False
    if len(a.xs) != len(b.xs):
        print(f"NODES MISMATCH {len(a.xs)} <> {len(b.xs)}")
        return False
    for i in range(0, len(a.xs)):
        aa = a.xs[i]
        bb = b.xs[i]
        if type(aa) is str:
            if type(bb) is str:
                if aa != bb:
                    return False
            else:
                return False
        elif type(bb) is str:
            return False
        else:
            if not are_equal(as_node(a.xs[i]), as_node(b.xs[i])):
                return False
    return True


