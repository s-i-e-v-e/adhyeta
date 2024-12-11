'''
Take Project Gutenberg text files convert it into
markup usable for further processing
Some manual fixup will be necessary before file is usable
'''
import copy

from mod.config import env
from mod.lib import fs, list_optional_append, sxml, list_head
from mod.lib.text import make_slug
from mod.root.backend.importers.tp import __get_works_list, __gut_raw_base
import re

cwd = f'{env.CACHE_ROOT}/gutenberg'

def __work_file(id: str) -> str:
    return f'{cwd}/{id}.txt'

def __collapse_newlines(text: str) -> str:
    pattern = re.compile(r'(\S)\n(\S)')
    result = pattern.sub(r'\1 \2', text)
    return result
def __match_chapters(text: str) -> str:
    pattern = re.compile(r'\n\n\n\n+')
    result = pattern.sub(r'\n</chapter>\n<chapter>\n<title>', text)
    return result
def __match_paras(text: str) -> str:
    pattern = re.compile(r'\n\n+([^\n]+)')
    result = pattern.sub(r'\n\n<p>\1</p>', text)
    return result
def __match_em(text: str) -> str:
    pattern = re.compile(r'_([^_]+)_')
    result = pattern.sub(r'<em>\1</em>', text)
    return result
def __match_hr(text: str) -> str:
    pattern = re.compile(r'\n\s*\*\s+\*\s+\*\s+\*\s+\*\s*\n')
    result = pattern.sub(r'\n\n<hr/>\n\n', text)
    return result

def __fix(id: str):
    fp = __work_file(id)
    qt = fs.read_text(fp)
    idx = qt.find('*** END OF THE PROJECT GUTENBERG')
    qt = qt[:idx]
    qt = qt.replace('\r\n', '\n')
    qt = __collapse_newlines(qt)
    qt = __match_em(qt)
    qt = __match_hr(qt)
    qt = __match_chapters(qt)
    qt = __match_paras(qt)
    qt =  f'<document><meta><copyright>CC0/PD. No rights reserved</copyright><source url="https://www.gutenberg.org/ebooks/{id}">Project Gutenberg</source>\n<title></title>\n<author></author>\n<category>\n<br/></category></meta>{qt}</document>'
    qt = qt.replace('>\n\n<', '>\n<')
    qt = qt.replace('<p><hr/></p>', '<hr/>')
    fs.write_text(fp.replace('.txt', '.xml'), qt)

def __split(id: str):
    from mod.lib import uuid
    dest_dir = f'{__gut_raw_base()}/{id}'
    fp = f'{__gut_raw_base()}/{id}.xml'
    xml_text = fs.read_text(fp)
    doc = sxml.from_xml(xml_text)
    cdoc.attrs['uuid'] = uuid.gen()

    toc_refs = []
    for c in doc.all('chapter'):
        cdoc = sxml.parse('(document (meta))')
        cdoc.attrs['uuid'] = uuid.gen()

        meta = cdoc.node(0)
        meta.append(doc.first('meta/copyright'))
        meta.append(doc.first('meta/source'))

        title = c.first('title')
        assert title
        c.remove(title)
        meta.append(title)
        assert meta.node(0).id == 'copyright'
        assert meta.node(1).id == 'source'
        assert meta.node(2).id == 'title'

        cdoc.append(c)
        chapter_file = f'{make_slug(title.value())}.xml'
        df = f'{dest_dir}/{chapter_file}'
        fs.write_text(df, sxml.to_xml(cdoc))

        ref = copy.deepcopy(title)
        ref.id = 'ref'
        ref.attrs['url'] = chapter_file
        toc_refs.append(ref)
    df = f'{dest_dir}/index.xml'
    doc.xs = [doc.first('meta')]
    toc_xml = f'<toc>\n{'\n'.join([sxml.to_xml(x) for x in toc_refs])}</toc>'
    toc = sxml.from_xml(toc_xml)
    doc.append(toc)
    fs.write_text(df, sxml.to_xml(doc))

def __download(id: str):
    fp = __work_file(id)
    fs.ensure_parent(fp)
    if fs.exists(fp):
        return

    url = f"https://www.gutenberg.org/ebooks/{id}.txt.utf-8"
    fs.exec(['wget', url, '--output-document', fp], cwd)

def process(file: str):
    WORKS = __get_works_list('gutenberg', file)
    for id in WORKS:
        fp = f'{__gut_raw_base()}/{id}.xml'
        if fs.exists(fp):
            print(f'splitting {id}')
            __split(id)
        else:
            print(f'downloading {id}')
            __download(id)
            __fix(id)
