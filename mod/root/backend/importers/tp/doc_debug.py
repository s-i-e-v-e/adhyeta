from mod.config import env
from mod.lib import sxml, fs


def __traverse(n: sxml.SxmlNode, level: int, ys: list[str]):
    prefix = ' ' * level
    xs = prefix+'['
    xs += n.id
    xs += ']'
    xs += ' '
    if 'text/css' not in n.attrs.values():
        for a in n.attrs:
            xs += f'{a}={n.attrs[a]}'
            xs += ' -- '
    ys.append(xs)
    for a in n.xs:
        if type(a) is str:
            ys.append(' '+prefix+'STR')
        else:
            __traverse(a, level+1, ys)

def debug(work: str, sf: str, doc: sxml.SxmlNode):
    ys = []
    __traverse(doc, 0, ys)
    fs.write_text(f'{env.CACHE_ROOT}/se-schema/{work}/{sf}.log', '\n'.join(ys))
