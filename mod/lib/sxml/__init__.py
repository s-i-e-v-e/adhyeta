from typing import Any, LiteralString, Optional

from mod.lib import text
from mod.lib.sxml.parser import SxmlNode, parse
from mod.lib.sxml.traverse import sxml_traverse
from mod.lib.sxml.filter import sxml_filter_node, sxml_get_str_node_val, sxml_index_of, sxml_insert_node, sxml_is_action, sxml_is_sym, \
    sxml_move_node_to, sxml_move_node_to_end, sxml_node_as_str, sxml_replace_node, sxml_node_exists,  are_equal, as_node, as_str

traverse = sxml_traverse
filter_node = sxml_filter_node
move_node_to = sxml_move_node_to
move_node_to_end = sxml_move_node_to_end
replace_node = sxml_replace_node
node_as_str = sxml_node_as_str
get_str_node_val = sxml_get_str_node_val
is_sym = sxml_is_sym
is_action = sxml_is_action
insert_node = sxml_insert_node
index_of = sxml_index_of
node_exists = sxml_node_exists


def unparse(x: SxmlNode | str) -> str:
    qs = []
    if type(x) is str:
        return text.sxml_el_escape(x)
    else:
        x = as_node(x)
        qs.append('(')
        qs.append(x.id)
        for a in x.attrs:
            qs.append(' @')
            qs.append(a)
            v = x.attrs[a]
            v = v if v else ''
            v = text.sxml_attr_escape(v)
            qs.append(' ')
            qs.append('"')
            qs.append(v)
            qs.append('"')
        if len(x.xs):
            qs.append(' ')
        for a in x.xs:
            qs.append(unparse(a))
        qs.append(')')
    return ''.join(qs)

FULL_BLOCK_ELEMENTS = 'div article section document meta toc header footer table chapter ul ol verse song letter poem dedication introduction'.split(' ')
BLOCK_ELEMENTS = 'hr ref li p tr blockquote title subtitle bridgehead author copyright source original category note'.split(' ')
BLOCK_ELEMENTS.extend(FULL_BLOCK_ELEMENTS)

def xml_prettify(x: str) -> str:
    return to_xml(from_xml(x))

def add_newline(x: SxmlNode, qs: list[str], es: list[LiteralString]):
    if x.id in es:
        qs.append('\n')

def __to_xml(x: SxmlNode|str) -> str:
    from mod.lib import text
    qs = []
    if type(x) is str:
        return text.xml_el_escape(x)
    else:
        x = as_node(x)
        if x.id == 'q':
            qs.append('(')
            for a in x.xs:
                qs.append(to_xml(a))
            qs.append(')')
        else:
            add_newline(x, qs, BLOCK_ELEMENTS)
            qs.append('<')
            qs.append(x.id)
            for a in x.attrs:
                qs.append(' ')
                qs.append(a)
                v = x.attrs[a]
                v = v if v else ''
                qs.append('=')
                qs.append('"')
                qs.append(text.xml_attr_escape(unparse(v)))
                qs.append('"')

            if x.xs:
                qs.append('>')
                add_newline(x, qs, FULL_BLOCK_ELEMENTS)
                for a in x.xs:
                    v = __to_xml(a)
                    if type(a) is SxmlNode and a.id in BLOCK_ELEMENTS:
                        if qs[-1] == ' ':
                            qs.pop()
                    qs.append(v)
            if x.xs:
                add_newline(x, qs, FULL_BLOCK_ELEMENTS)
                qs.append('</')
                qs.append(x.id)
                qs.append('>')
            else:
                qs.append('/>')
                add_newline(x, qs, FULL_BLOCK_ELEMENTS)

    return ''.join(qs)

def to_xml(x: SxmlNode|str) -> str:
    import re
    xml = __to_xml(x).strip()
    xml = re.sub(r'\n+', '\n', xml)
    return xml

def from_xml(x: str) -> SxmlNode:
    import re
    x = re.sub(r'\s+', ' ', x)
    from lxml import etree
    from mod.lib import text
    def traverse_node(n: etree.ElementBase, xs: list[str]):
        xs.append('(')
        tag = 'sq' if n.tag == 'q' else n.tag
        xs.append(tag)
        for k, v in n.attrib.items():
            xs.append(' @')
            xs.append(k)
            xs.append(' ')
            xs.append('"')
            xs.append(text.sxml_attr_escape(v))
            xs.append('"')
        if n.text:
            xs.append(' ')
            xs.append(text.sxml_el_escape(n.text))
        for c in n:
            traverse_node(c, xs)
        xs.append(')')
        if n.tail:
            xs.append(text.sxml_el_escape(n.tail))
        assert type(xs[-1]) is str

    xs = []
    try:
        n = etree.fromstring(x)
        etree.strip_elements(n, etree.Comment)
        traverse_node(n, xs)
    except Exception as e:
        raise e
    yy = ''.join(xs).replace('\n)', ')')
    return parse(yy)

def is_node(n: SxmlNode|str) -> bool:
    return type(n) is SxmlNode