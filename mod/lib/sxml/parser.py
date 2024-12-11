from dataclasses import dataclass
from mod.lib.sxml.ps import ParserState

@dataclass
class Token:
    type: str
    xs: str|list

SxmlChildNodes = list['SxmlNode|str']
@dataclass
class SxmlNode:
    path: str
    line: int
    id: str
    attrs: dict[str, str]
    xs: SxmlChildNodes

def _has(xs: list, x: str) -> bool:
    return True if not len(xs) else any([x in y for y in xs])

def _is_ws(x: str) -> bool:
    return _has([' ', '\n', '\t'], x)

def _parse_ws(ps: ParserState):
    xs = ''
    while not ps.eos():
        x = ps.peek()
        if not _is_ws(x):
            break
        xs += ps.next()
    return xs

_skip_ws = _parse_ws

# can contain anything except `(` OR `)`
def parse_id(ps: ParserState):
    xs = ''
    while not ps.eos():
        x = ps.peek()
        if _is_ws(x) or x in "()":
            break
        xs += ps.next()
    return xs

def _parse_str(ps: ParserState):
    # "
    ps.next()

    xs = ''
    while not ps.eos():
        x = ps.next()
        if x == '"':
            break
        xs += x
    return xs.strip()

# can contain anything except `"` OR `(` OR `)`
def _parse_unquoted_str(ps: ParserState, break_on = ""):
    xs = ''
    while not ps.eos():
        x = ps.peek()
        if x in ["\"", "(", ")"] or x in break_on:
            break
        xs += ps.next()
    return xs

def _parse_attrs(ps: ParserState):
    xs = {}
    while not ps.eos():
        x = ps.peek()
        if x != '@':
            break

        # @
        ps.next()
        k = parse_id(ps)
        _skip_ws(ps)

        v = ''
        # is an action
        if k.startswith("x-"):
            pass
        else:
            # check for empty attr
            x = ps.peek()
            if x == '@':
                pass
            else:
                if x == '"':
                    v = _parse_str(ps)
                else:
                    v = _parse_unquoted_str(ps, "@\n ")
                _skip_ws(ps)
        xs[k] = v

    return xs

def add_if_not_empty(xs: SxmlChildNodes, y: str):
    import re
    y = re.sub(r"\s*\n+\s*", "\n", y)
    if y:
        xs.append(y)

def _parse_list(ps: ParserState, parent: str):
    # (
    ps.next()

    start = ps.i
    id = parse_id(ps)
    y = SxmlNode(f"{parent}/{id}", start, id, {}, [])
    _skip_ws(ps)

    y.attrs = _parse_attrs(ps)

    x = ''
    while not ps.eos():
        s = _parse_ws(ps)
        add_if_not_empty(y.xs, s)

        x = ps.peek()
        if x == '"':
            s = _parse_str(ps)
            add_if_not_empty(y.xs, s)
        elif x == '(':
            y.xs.append(_parse_list(ps, y.path))
        elif x == ")":
            x = ps.next()
            break
        else:
            s = _parse_unquoted_str(ps)
            add_if_not_empty(y.xs, s)

    if x != ')':
        raise ps.error(f"incomplete list: {y.id}", start)

    return y


def sxml_parse(text: str):
    ps = ParserState(text
                     .replace("\r\n", "\n")
                     .replace("\r", "\n")
                     .replace("\t", " ")
                     )

    _skip_ws(ps)

    if ps.eos():
        raise ps.error("stream is empty", 0)

    x = ps.peek()
    if x != '(':
        raise ps.error( f"invalid token: `{x}`", 0)

    y = _parse_list(ps, "")
    _skip_ws(ps)

    if not ps.eos():
        raise ps.error("stream not yet consumed", 0)

    return y