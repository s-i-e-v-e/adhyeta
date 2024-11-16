from dataclasses import dataclass


@dataclass
class ParserState:
    i: int
    max: int
    xx: str

@dataclass
class Token:
    type: str
    lexeme: str

def ps_peek(ps: ParserState):
    return ps.xx[ps.i]

def ps_next(ps: ParserState):
    x = ps.xx[ps.i]
    ps.i += 1
    return x

def _is_num(x: str) -> bool:
    return any([x in y for y in "0123456789"])

def _is_ws(x: str) -> bool:
    return any([x in y for y in [' ', '\r', '\n', '\t']])

def _parse_ws(ps: ParserState):
    while True:
        x = ps_peek(ps)
        if not _is_ws(x):
            break
        ps_next(ps)

def _parse_unit(ps: ParserState, type: str):
    xs = ''
    while ps.i < ps.max:
        x = ps_peek(ps)
        if _is_ws(x):
            ps_next(ps)
            break
        ps_next(ps)
        xs += x
    return Token(type, xs)

def _parse_str(ps: ParserState):
    ps_next(ps)

    xs = ''
    while True:
        x = ps_next(ps)
        if x == '"':
            break
        xs += x
    return Token('str', xs)

def _parse_kv(ps: ParserState):
    ps_next(ps)

    k = _parse_unit(ps, 'attr')
    _parse_ws(ps)
    v = _parse_unit(ps, 'val')
    return k, v

def _parse_item(ps: ParserState):
    x = ps_peek(ps)
    if x == '@':
        return _parse_kv(ps)
    elif x == '"':
        return _parse_str(ps)
    else:
        return _parse_unit(ps, 'str')

def _parse_list(ps: ParserState):
    ps_next(ps)

    xs = []
    xs.append(Token('(', ''))

    id = ps_next(ps)
    xs.append(Token('id', id))
    _parse_ws(ps)

    while ps.i < ps.max:
        x = ps_peek(ps)
        if x == ")":
            ps_next(ps)
            xs.append(Token(')', ''))
            break
        xs.append(_parse_item(ps))
    return xs

def _parse(ps: ParserState):
    xs = []
    while ps.i < ps.max:
        _parse_ws(ps)
        x = ps_peek(ps)
        if x == '(':
           xs.extend(_parse_list(ps))
    return xs

def sxml_parse(xx: str):
    ps = ParserState(0, len(xx), xx)
    print(_parse(ps))


if __name__ == '__main__':
    sxml_parse('(p @id 45 this is a sentence.')