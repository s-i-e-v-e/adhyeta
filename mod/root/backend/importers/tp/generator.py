from mod.config import env
from mod.lib import fs, sxml, text
from mod.lib.sxml.parser import SxmlNode
from mod.root.backend.importers.tp import __gut_raw_base, __se_raw_base, __ref_to_slug


def __generate_chapter(sf: str, df: str):
    n = sxml.from_xml(fs.read_text(sf))
    chapter = n.node(1)
    chapter.id = 'matter'
    chapter.attrs['type'] = 'chapter'
    fs.write_text(df, sxml.unparse(n))

def __generate_project(parent: str, target: str):
    print('generating ' + parent)

    en_index_file = f'{parent}/index.xml'
    sa_index_file = f'{parent}/index.sa.xml'

    doc_en = sxml.from_xml(fs.read_text(en_index_file))
    doc_sa = sxml.from_xml(fs.read_text(sa_index_file))

    # generate index
    title = doc_sa.first_('meta/title').value_rec()
    author_node = doc_en.first_('meta/author')
    if 'use' in author_node.attrs:
        author = author_node.attrs['use']
    else:
        author = author_node.value_rec()
    slug_t = text.make_slug(title)
    slug_a = text.make_slug(author)
    url_base = f'{target}/{slug_a}/{slug_t}'
    toc = doc_sa.node(1)

    for i, r in enumerate(toc.xs):
        assert isinstance(r, SxmlNode)
        slug_v = __ref_to_slug(r.value_rec(), r.attrs.get('label', ''), r.attrs.get('n', ''))

        url = f'{url_base}/{slug_v}.sxml'
        sf = f'{parent}/{text.sxml_attr_escape(r.attrs.pop('url'))}'
        df = f'{env.SXML_ROOT}{url}'

        r.id = 'a'
        r.attrs['href'] = url
        __generate_chapter(sf, df)
        toc.xs[i] = sxml.parse('(lit)')
        toc.xs[i].append(r)

    doc_sa.xs[1] = sxml.parse('(matter @type toc)')
    doc_sa.xs[1].append(toc)

    meta = doc_sa.node(0)
    orig = meta.first('original')
    if orig:
        v = f'{orig.node(0).value()} BY {orig.node(1).value()}'
        orig.xs = [v]

    df = f'{env.SXML_ROOT}{url_base}/index.sxml'
    fs.write_text(df, sxml.unparse(doc_sa))

def __generate(dp: str, target = '', base = ''):
    for f in fs.list_files(dp):
        if f.name == 'index.sa.xml':
            __generate_project(dp, target)
        elif f.name == 'index.sxml':
            doc = sxml.parse(fs.read_text(f.full_path))
            target = doc.attrs['target']
            index_file = f'{env.SXML_ROOT}{target}{base}/{f.name}'
            print('copying ' + index_file.replace(env.SXML_ROOT, ''))
            fs.copy_file(f.full_path, index_file)

    for f in fs.list_dirs(dp):
        __generate(f.full_path, target, f'{base}/{f.name}')

def generate_se():
    __generate(__se_raw_base())

def generate_gut():
    __generate(__gut_raw_base())