from mod.config import env
from mod.lib import fs, sxml
from mod.lib.sxml.parser import SxmlNode
from mod.lib.text import make_slug
from mod.root.backend.importers.tp.work_uuids import __get_uuids_for_work

ROOT = f'{env.RAW_ROOT}/gutenberg'

def __process_doc(sf: str, uuid: str, BASE_OUT: str):
    n = sxml.from_xml(fs.read_text(sf))
    n.attrs['uuid'] = uuid

    _, title = sxml.filter_node(n, '/document/title')
    slug = make_slug(title.xs[0])
    df = f"{BASE_OUT}/{slug}.sxml"

    xs = sxml.unparse(n)
    fs.write_text(df, xs)
    return slug

def __process_work(work: str):
    BASE = f'{ROOT}/{work}'
    uuids = __get_uuids_for_work(f'{BASE}/ids')

    wn = sxml.from_xml(fs.read_text(f'{BASE}/index.xml'))
    wn.attrs['uuid'] = uuids.pop()
    _, book_title = sxml.filter_node(wn, '/document/title')
    _, book_author = sxml.filter_node(wn, '/document/author')
    _, toc = sxml.filter_node(wn, '/document/toc')

    SA_OUT = f'/sa/p/{make_slug(book_author.xs[0])}/{make_slug(book_title.xs[0])}'
    BASE_OUT = f'{env.SXML_ROOT}{SA_OUT}'
    toc.id = 'matter'
    ul = sxml.parse('(ul)')
    ul.xs = toc.xs
    toc.xs = [ul]

    for i in range(0, len(ul.xs)):
        y = ul.xs[i]
        if type(y) is not SxmlNode:
            continue

        url = y.attrs.pop('url')
        sf = f"{BASE}/{url}"
        slug =__process_doc(sf, uuids.pop(), BASE_OUT)

        y.id = 'a'
        y.attrs['href'] = f'{SA_OUT}/{slug}.sxml'
        yy = sxml.parse('(li)')
        yy.xs.append(y)
        ul.xs[i] = yy

    xs = sxml.unparse(wn)
    df = f'{BASE_OUT}/index.sxml'
    fs.write_text(df, xs)

def process():
    for f in fs.list_dirs(ROOT):
        __process_work(f.name)