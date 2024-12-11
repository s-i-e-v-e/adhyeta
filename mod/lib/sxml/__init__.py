from typing import Any

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
        return x
    else:
        x = as_node(x)
        qs.append('(')
        qs.append(x.id)
        for a in x.attrs:
            qs.append(' @')
            qs.append(a)
            v = x.attrs[a]
            v = v if v else ''
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

def to_xml(x: SxmlNode|str) -> str:
    from mod.lib import text
    qs = []
    if type(x) is str:
        return x
    else:
        x = as_node(x)
        if x.id == 'q':
            qs.append('(')
            for a in x.xs:
                qs.append(to_xml(a))
            qs.append(')')
        else:
            qs.append('<')
            qs.append(x.id)
            for a in x.attrs:
                qs.append(' ')
                qs.append(a)
                v = x.attrs[a]
                v = v if v else ''
                qs.append('=')
                qs.append('"')
                qs.append(text.xml_escape(unparse(v)))
                qs.append('"')
            qs.append('>')
            for a in x.xs:
                qs.append(to_xml(a))
            qs.append('</')
            qs.append(x.id)
            qs.append('>')
    return ''.join(qs)

def from_xml(x: str) -> SxmlNode:
    from lxml import etree
    from mod.lib import text
    def traverse_node(n: etree.ElementBase, xs: list[str]):
        xs.append('(')
        xs.append(n.tag)
        for k, v in n.attrib.items():
            xs.append(' @')
            xs.append(k)
            xs.append(' ')
            xs.append('"')
            xs.append(text.xml_escape(v))
            xs.append('"')
        if n.text:
            n.text = n.text.replace('(', '(q ')
            xs.append(' ')
            xs.append(n.text)
        for c in n:
            traverse_node(c, xs)
        xs.append(')')
        if n.tail:
            n.tail = n.tail.replace('(', '(q ')
            xs.append(n.tail)

    xs = []
    traverse_node(etree.fromstring(x), xs)
    yy = ''.join(xs).replace('\n)', ')')
    return parse(yy)
