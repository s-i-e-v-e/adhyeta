from dataclasses import dataclass
from posixpath import ismount
from shutil import Error
from typing import Any, Callable
import typing

@dataclass
class ParserState:
    i: int
    max: int
    xx: str

@dataclass
class Token:
    type: str
    xs: str|list

@dataclass
class SxmlNode:
    line: int
    id: str
    attrs: dict[str, str]
    xs: list

def ps_error(ps: ParserState, m: str, idx: int):
    idx = idx if idx else ps.i
    line = 1 + ps.xx.count('\n', 0, idx)
    a = ps.xx.rfind('\n', 0, idx)
    b = ps.xx.find('\n', idx)
    char = idx - a
    x = ps.xx[idx:b]
    return Error(f"{m}: {x} (L{line}C{char})")

def ps_eos(ps: ParserState):
    return ps.i >= ps.max

def ps_peek(ps: ParserState):
    if ps_eos(ps):
        return ''
    return ps.xx[ps.i]

def ps_next(ps: ParserState):
    if ps_eos(ps):
        return ''
    x = ps.xx[ps.i]
    ps.i += 1
    return x

def _has(xs: list, x: str) -> bool:
    return True if not len(xs) else any([x in y for y in xs])

def _is_ws(x: str) -> bool:
    return _has([' ', '\r', '\n', '\t'], x)

def _parse_ws(ps: ParserState):
    xs = ''
    while not ps_eos(ps):
        x = ps_peek(ps)
        if not _is_ws(x):
            break
        xs += ps_next(ps)
    return xs

def _parse_unit(ps: ParserState, break_on: list):
    xs = ''
    while not ps_eos(ps):
        x = ps_peek(ps)
        if _is_ws(x) or _has(break_on, x):
            break
        xs += ps_next(ps)
    return xs

def _parse_str(ps: ParserState):
    ps_next(ps)

    xs = ''
    while not ps_eos(ps):
        x = ps_next(ps)
        if x == '"':
            break
        xs += x
    return xs

def _parse_attrs(ps: ParserState):
    xs = {}
    while not ps_eos(ps):
        x = ps_peek(ps)
        if x != '@':
            break

        ps_next(ps)
        k = _parse_unit(ps, ['(', ')'])
        _parse_ws(ps)

        if k.startswith("x-"):
            v = ''
        else:
            # check for empty attr
            x = ps_peek(ps)
            v = ''
            if x != '@':
                if x == '"':
                    v = _parse_str(ps)
                else:
                    v = _parse_unit(ps, ['(', ')'])
                _parse_ws(ps)
            else:
                pass
        xs[k] = v

    return xs

def _parse_list(ps: ParserState):
    ps_next(ps)

    start = ps.i
    y = SxmlNode(start, '', {}, [])
    y.id = _parse_unit(ps, ['(', ')'])
    _parse_ws(ps)

    x = ps_peek(ps)
    if x == '@':
        y.attrs = _parse_attrs(ps)

    x = ''
    while not ps_eos(ps):
        y.xs.append(_parse_ws(ps))
        x = ps_peek(ps)
        if x == '"':
            y.xs.append(_parse_str(ps))
        elif x == '(':
            y.xs.append(_parse_list(ps))
        elif x == ")":
            x = ps_next(ps)
            break
        else:
            y.xs.append(_parse_unit(ps, ['(', ')']))

    if x != ')':
        print(y)
        raise ps_error(ps, f"incomplete list: {y.id}", start)
    return y

def _parse(ps: ParserState):
    _parse_ws(ps)

    if ps_eos(ps):
        return None

    x = ps_peek(ps)
    if x != '(':
        raise ps_error(ps, f"invalid token: `{x}`", 0)
    y = _parse_list(ps)
    _parse_ws(ps)

    if not ps_eos(ps):
        raise ps_error(ps, f"stream not yet consumed", 0)
    return y

def sxml_parse(xx: str):
    xx = xx.replace("\r\n", "\n").replace("\r", "\n")
    ps = ParserState(0, len(xx), xx)
    return _parse(ps)


def sxml_traverse(x: SxmlNode, indent: int, y: Any, fn: Callable[[SxmlNode|str, int, Any, str], Any|None]):
    yq = fn(x, indent, y, "B")
    if not yq:
        return

    if type(x) == SxmlNode:
        for xx in x.xs:
            sxml_traverse(xx, indent + 1, yq, fn)
    fn(x, indent, y, "E")

def sxml_ast_dump(x: SxmlNode, indent: int = 0):
    prefix = "-" * indent if indent else ""
    print(f"{prefix}LIST_{x.id}")
    for k in x.attrs:
        print(f"{prefix}@{k}:{x.attrs[k]}")
    for v in x.xs:
        if type(v) is str:
            print(f"{prefix}{v}")
        else:
            sxml_ast_dump(v, indent + 1)

SxmlNodePair = tuple[SxmlNode|None, SxmlNode|None]
def _filter_node(p: SxmlNode|None, x: SxmlNode, i: int, qs: list[str]) -> SxmlNodePair:
    if qs[i] in x.id:
        if i < len(qs)-1:
            for y in x.xs:
                if type(y) == str:
                    continue
                zp, zx = _filter_node(x, y, i + 1, qs)
                if zx:
                    return zp, zx
        else:
            return p, x
    return p, None

def filter_node(x: SxmlNode, q: str) -> SxmlNodePair:
    q = q[1:]
    p, y = _filter_node(None, x, 0, q.split("/"))
    return p, y

def sxml_remove_node(x: SxmlNode, q: str):
    p, y = filter_node(x, q)
    if not p or not y:
        return
    p.xs.remove(y)
    return y

def sxml_move_node_to_end(x: SxmlNode, q: str):
    y = sxml_remove_node(x, q)
    if not y:
        return
    x.xs.append(y)

def sxml_replace_node(x: SxmlNode, q: str, z: SxmlNode):
    p, y = filter_node(x, q)
    if not p or not y:
        return
    i = p.xs.index(y)
    p.xs[i] = z

def sxml_get_str_node_val(x: SxmlNode, q: str):
    _, y = filter_node(x, q)
    if not y:
        return
    for a in y.xs:
        if type(a) != str:
            raise Error(f"Bad Node {q} [{type(a).__name__}]")

    return " ".join(y.xs).strip()
