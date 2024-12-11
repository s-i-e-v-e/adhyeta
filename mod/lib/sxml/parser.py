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

def __has(xs: list, x: str) -> bool:
    return True if not len(xs) else any([x in y for y in xs])

def __parse_ws(ps: ParserState):
    xs = ''
    while not ps.eos():
        x = ps.peek()
        if x != ' ':
            break
        xs += ps.next()
    return xs

_skip_ws = __parse_ws

# can contain anything except `(` OR `)`
def __parse_id(ps: ParserState):
    xs = ''
    while not ps.eos():
        x = ps.peek()
        if x in " ()":
            break
        xs += ps.next()
    return xs

def __parse_quoted_str(ps: ParserState):
    start = ps.i
    # "
    ps.next()

    xs = ''
    while not ps.eos():
        x = ps.next()
        if x == '\\':
            x = ps.next()
            if x != '"':
                raise ps.error(f"invalid string escape", start)
        elif x == '"':
            break
        xs += x
    return xs.strip()

# can contain anything except `(` OR `)`
def __parse_text(ps: ParserState, break_on =""):
    xs = ''
    while not ps.eos():
        x = ps.peek()
        if x in ["(", ")"] or x in break_on:
            break
        xs += ps.next()
    return xs

def __parse_attrs(ps: ParserState):
    xs = {}
    while not ps.eos():
        x = ps.peek()
        if x != '@':
            break

        # @
        ps.next()
        k = __parse_id(ps)
        _skip_ws(ps)

        v = ''
        # check for empty attr
        x = ps.peek()
        if x == '@':
            pass
        else:
            if x == '"':
                v = __parse_quoted_str(ps)
            else:
                v = __parse_text(ps, "@ ")
            _skip_ws(ps)
        xs[k] = v

    return xs

def __add_if_not_empty(xs: SxmlChildNodes, y: str):
    import re
    y = re.sub(r"\s+", " ", y)
    if y:
        if xs and type(xs[-1]) is str:
            xs[-1] += y
            return
        xs.append(y)

def __parse_list(ps: ParserState, parent: str):
    # (
    ps.next()

    start = ps.i
    id = __parse_id(ps)
    y = SxmlNode(f"{parent}/{id}", start, id, {}, [])
    _skip_ws(ps)

    y.attrs = __parse_attrs(ps)

    x = ''
    while not ps.eos():
        __add_if_not_empty(y.xs, __parse_ws(ps))

        x = ps.peek()
        if x == '(':
            y.xs.append(__parse_list(ps, y.path))
        elif x == ")":
            x = ps.next()
            break
        else:
            __add_if_not_empty(y.xs, __parse_text(ps))

    if x != ')':
        raise ps.error(f"incomplete list: {y.id}. found: {x} = {hex(ord(x))}", start)

    if y.xs:
        if type(y.xs[0]) is str and y.xs[0].lstrip() == '':
            y.xs.reverse()
            y.xs.pop()
            y.xs.reverse()
    if y.xs:
        if type(y.xs[-1]) is str:
            y.xs[-1] = y.xs[-1].rstrip()
            if not y.xs[-1]:
                y.xs.pop()
    return y


def dump_ast(x: SxmlNode, indent: int = 0):
    prefix = "-" * indent if indent else ""
    print(f"{prefix}LIST_{x.id}")
    for k in x.attrs:
        print(f"{prefix}@{k}:{x.attrs[k]}")
    for v in x.xs:
        if type(v) is str:
            print(f"{prefix}{v}")
        else:
            dump_ast(v, indent + 1)

def parse(text: str) -> SxmlNode:
    ps = ParserState(text
                     .replace("\r\n", " ")
                     .replace("\r", " ")
                     .replace("\n", " ")
                     .replace("\t", " ")
                     )

    _skip_ws(ps)

    if ps.eos():
        raise ps.error("stream is empty", 0)

    x = ps.peek()
    if x != '(':
        raise ps.error( f"invalid token: `{x}`", 0)

    y = __parse_list(ps, "")
    _skip_ws(ps)

    if not ps.eos():
        dump_ast(y)
        print(ps.peek())
        raise ps.error("stream not yet consumed", 0)

    return y