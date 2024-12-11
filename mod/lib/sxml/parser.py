import typing
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

    def is_str(self, i: int) -> bool:
        return isinstance(self.xs[i], str)

    def head(self):
        return self.xs[0]

    def node(self, i: int):
        return typing.cast(SxmlNode, self.xs[i])

    def list_nodes(self) -> list['SxmlNode']:
        from mod.lib import sxml
        return [x for x in self.xs if sxml.is_node(x)]

    def children_of(self, i: int):
        return self.node(i).xs

    def string(self, i: int):
        return self.xs[i]

    def value(self):
        assert len(self.xs) == 1
        assert type(self.xs[0]) is str
        return self.xs[0]

    def value_rec(self):
        xx = ''
        for x in self.xs:
            if isinstance(x, str):
                xx += x
            else:
                xx += x.value_rec()
        return xx

    def append(self, x: 'SxmlNode|None'):
        if x:
            self.xs.append(x)

    def remove(self, x: 'SxmlNode'):
        self.xs.remove(x)

    def first(self, q: str):
        xs = self.all(q)
        return xs[0] if xs else None

    def first_(self, q: str):
        x = self.first(q)
        assert x is not None
        return x

    def all(self, q: str):
        def __query_all(n: SxmlNode, i: int, qs: list[str]):
            if n.id != qs[i]:
                return []

            last = len(qs) - 1
            if i == last:
                return [n]

            zs = []
            for x in [x for x in n.xs if type(x) is SxmlNode]:
                xs = __query_all(x, i + 1, qs)
                if xs:
                    zs.extend(xs)
            return zs

        qs = f'{self.id}/{q}'.split('/')
        return __query_all(self, 0, qs)


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
        if x in ["\\", "(", ")"] or x in break_on:
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

def __append_str(xs: SxmlChildNodes, y: str):
    if xs and type(xs[-1]) is str:
        xs[-1] += y
        return
    xs.append(y)

def __add_if_not_empty(xs: SxmlChildNodes, y: str):
    import re
    y = re.sub(r"\s+", " ", y)
    if y:
        __append_str(xs, y)

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
        if x == '\\':
            ps.next()
            __append_str(y.xs, ps.next())
        elif x == '(':
            y.xs.append(__parse_list(ps, y.path))
        elif x == ")":
            x = ps.next()
            break
        else:
            __add_if_not_empty(y.xs, __parse_text(ps))

    if x != ')':
        print(y.xs)
        print(f'EOS {ps.eos()}')
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

    return __trim(y)

PRESERVE_SPACES_FOR = 'i b em strong w corr sic q " \''.split(' ')
def __trim(n: SxmlNode):
    def previous(i: int):
        if i - 1 >= 0:
            return n.xs[i-1]
        else:
            return ''

    removals = []
    for i, c in enumerate(n.xs):
        p = previous(i)
        if type(c) is SxmlNode and c.id not in PRESERVE_SPACES_FOR and type(p) is str and p == ' ':
            removals.append(i-1)
    removals.reverse()
    for i in removals:
        n.xs.pop(i)

    for c in n.xs:
        if type(c) is SxmlNode:
            __trim(c)
    return n
