from dataclasses import dataclass
from shutil import Error

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
class List:
    id: str
    attrs: dict
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

    y = List('', {}, [])

    start = ps.i
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


def sxml_ast_dump(x: List, indent: int):
    prefix = "-" * indent if indent else ""
    print(f"{prefix}LIST_{x.id}")
    for k,v in x.attrs:
        print(f"{prefix}@{k}:{v}")
    for v in x.xs:
        if type(v) is str:
            print(f"{prefix}{v}")
        else:
            sxml_ast_dump(v, indent + 1)

if __name__ == '__main__':
    z = sxml_parse('(p @id 45 this is a sentence.)')
    print(z)