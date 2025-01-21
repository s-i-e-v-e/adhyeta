import dataclasses
import pprint
import typing

from lxml import etree
import re

from mod.lib import text

@dataclasses.dataclass
class XmlNode:
    id: str
    attrs: dict[str, str]
    xs: list['XmlNode|str']

    def head(self):
        return self.xs[0]

    def value(self) -> str:
        assert len(self.xs) == 1
        return self.as_str(0)

    def value_rec(self):
        xx = ''
        for x in self.xs:
            if isinstance(x, str):
                xx += x
            elif isinstance(x, XmlNode):
                xx += x.value_rec()
            else:
                raise TypeError
        return xx

    def as_str(self, i: int):
        assert self.is_str(i)
        return typing.cast(str, self.xs[i])

    def is_str(self, i: int):
        return isinstance(self.xs[i], str)

    def is_node(self, i: int):
        return isinstance(self.xs[i], XmlNode)

    def node(self, i: int) -> 'XmlNode':
        assert isinstance(self.xs[i], XmlNode)
        return typing.cast(XmlNode, self.xs[i])

    def string(self, i: int) -> str:
        assert self.is_str(i)
        return typing.cast(str, self.xs[i])

    def list_nodes(self) -> list['XmlNode']:
        return [x for x in self.xs if isinstance(x, XmlNode)]

    def first(self, q: str):
        xs = self.all(q)
        return xs[0] if xs else None

    def first_(self, q: str):
        x = self.first(q)
        assert x is not None
        return x

    def all(self, q: str):
        def __query_all(n: XmlNode, i: int, qs: list[str]):
            if n.id != qs[i]:
                return []

            last = len(qs) - 1
            if i == last:
                return [n]

            zs = []
            for x in [x for x in n.xs if type(x) is XmlNode]:
                xs = __query_all(x, i + 1, qs)
                if xs:
                    zs.extend(xs)
            return zs

        qs = f'{self.id}/{q}'.split('/')
        return __query_all(self, 0, qs)

    def drop_child_where(self, k: str, v: str, level = 0):
        def drop_node(xs: list[XmlNode]):
            for x in xs:
                self.xs.remove(x)

        drop = []
        for x in self.list_nodes():
            q = x.drop_child_where(k, v, level + 1)
            if q:
                drop.append(q)
        drop_node(drop)

        for ak in self.attrs:
            if ak == k and self.attrs[ak] == v:
                return self

@dataclasses.dataclass
class Prettifier:
    blocks: list[str]
    full_blocks: list[str]

    @staticmethod
    def build(blocks: str, full_blocks: str) -> 'Prettifier':
        return Prettifier(blocks.split(' '), full_blocks.split(' '))

PRETTIFIER = Prettifier.build('', '')
def unparse(n: XmlNode, pp = PRETTIFIER):
    def add_newline(x: XmlNode, xs: list[str], es: list[str]):
        if x.id in es:
            while xs and xs[-1] in ['\n', ' ']:
                xs.pop(-1)
            xs.append('\n')

    def traverse_node(n: XmlNode, xs: list[str]):
        add_newline(n, xs, pp.blocks + pp.full_blocks)
        xs.append('<')
        xs.append(n.id)

        for k, v in n.attrs.items():
            xs.append(' ')
            xs.append(k)
            xs.append('="')
            xs.append(text.xml_attr_escape(v))
            xs.append('"')

        if n.xs:
            xs.append('>')
            add_newline(n, xs, pp.full_blocks)
            for c in n.xs:
                if isinstance(c, XmlNode):
                    traverse_node(c, xs)
                elif isinstance(c, str):
                    xs.append(text.xml_attr_escape(c))
                else:
                    raise Exception(type(c))

        if n.xs:
            add_newline(n, xs, pp.full_blocks)
            xs.append('</')
            xs.append(n.id)
            xs.append('>')
        else:
            xs.append('/>')
        add_newline(n, xs, pp.blocks + pp.full_blocks)

    xs = []
    traverse_node(n, xs)
    return ''.join(xs)

def parse(xml: str, pp = PRETTIFIER):
    xml = re.sub(r'\s+', ' ', xml)

    def traverse_node(n: etree.ElementBase):
        xn = XmlNode(n.tag, {}, [])
        for k, v in n.attrib.items():
            xn.attrs[k] = v

        if n.text:
            xn.xs.append(n.text)
        for c in n:
            cn, tail = traverse_node(c)
            xn.xs.append(cn)
            if tail:
                xn.xs.append(tail)

        return xn, n.tail

    def normalize(n: XmlNode):
        if n.xs:
            x = n.xs[0]
            if isinstance(x, str):
                x = x.lstrip()
                if x:
                    n.xs[0] = x
                else:
                    n.xs.pop(0)

            x = n.xs[-1]
            if isinstance(x, str):
                x = x.rstrip()
                if x:
                    n.xs[-1] = x
                else:
                    n.xs.pop(-1)

        for c in n.list_nodes():
            normalize(c)

        rm = []
        for i in range(0, len(n.xs)):
            if i > 0 and n.is_str(i-1) and n.is_node(i) and (n.node(i).id in pp.blocks or n.node(i).id in pp.full_blocks):
                x = n.as_str(i-1)
                assert x.strip() == ''
                rm.append(i-1)
        rm.reverse()
        for i in rm:
            n.xs.pop(i)

    try:
        n = etree.fromstring(xml)
        etree.strip_elements(n, etree.Comment)
        xn, tail = traverse_node(n)
        assert tail is None
        normalize(xn)
        return xn
    except Exception as e:
        pprint.pprint(xml)
        raise e