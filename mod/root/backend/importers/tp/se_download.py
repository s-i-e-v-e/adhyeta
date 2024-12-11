'''
Take Standard E-books PD content and convert it into
markup usable for further processing
'''
import re
from dataclasses import dataclass
from typing import Callable

from mod.config import env
from mod.lib import fs, sxml, text
from mod.root.backend.importers.tp import __get_works_list, __se_raw_base, project_uuids
from mod.lib.text import make_slug

@dataclass(init=True)
class SectionMeta:
    label: sxml.SxmlNode|None
    ordinal: sxml.SxmlNode|None
    title: sxml.SxmlNode|None
    subtitle: sxml.SxmlNode|None
    bridgehead: sxml.SxmlNode|None
    title_notes: list[sxml.SxmlNode]

@dataclass
class SeSource:
    base: str
    base_out: str
    work: str
    read_text: Callable[[str], str]
    write_text: Callable[[str, str], None]
    exists: Callable[[str], bool]

@dataclass
class SeChapter:
    title: str
    meta: SectionMeta|None
    xml: str

    def load(self):
        try:
            return sxml.from_xml(self.xml)
        except Exception as e:
            print(self.xml)
            raise e

    def write(self, ses: SeSource, df: str):
        xml = self.xml
        xml = re.sub(r'\s*<br/>\s*', '<br/>', xml)
        xml = xml.replace('<nop>', '').replace('</nop>', '')
        xml = xml.replace('<nop/>', '')
        xml = sxml.xml_prettify(xml)
        ses.write_text(df, xml)

    @staticmethod
    def from_file(ses: SeSource, sf: str, title: str):
        x = ses.read_text(sf)
        xs = x.splitlines()
        xs = xs[1:]
        xs[0] = '<html>'
        x = '\n'.join(xs)
        x = x.replace('epub:', '')
        x = x.replace('dc:', '')
        x = x.replace('xml:', '')
        x = re.sub(r'<abbr[^>]*>', '', x)
        x = x.replace('</abbr>', '')
        x = x.replace('type="fulltitle"', 'type="title"')
        # x = x.replace('<hgroup>', '')
        # x = x.replace('</hgroup>', '')
        return SeChapter(title, None, x)

@dataclass
class RefEntry:
    url: str
    label: str
    n: str
    title: str

FootNotes = dict[str, list[sxml.SxmlNode]]
@dataclass
class SeBook:
    work: str
    title: str
    author: str
    toc: list[RefEntry]
    footnotes: FootNotes
    chapters: list[SeChapter]


def __translate_note(n: sxml.SxmlNode, foot_notes: dict):
    if 'type' in n.attrs and n.attrs['type'] == 'noteref':
        assert n.id == 'a'
        n.id = 'fn'
        n.attrs.pop('href')
        n.attrs.pop('id')
        n.attrs.pop('type')
        n.attrs['n'] = n.value()
        n.xs = foot_notes[n.attrs['n']]

def __rewrite_note(n: sxml.SxmlNode, foot_notes: dict, level = 0):
    for x in n.list_nodes():
        __rewrite_note(x, foot_notes, level + 1)
    __translate_note(n, foot_notes)

def __drop_node(n: sxml.SxmlNode, k: str, v: str, level = 0):
    drop = []
    def drop_node():
        for d in drop:
            n.xs.remove(d)

    for x in n.list_nodes():
        q = __drop_node(x, k, v, level + 1)
        if q: drop.append(q)
    drop_node()

    for ak in n.attrs:
        if ak == k and n.attrs[ak] == v:
            if not level:
                drop.append(n)
                drop_node()
            return n

def __traverse_node(n: sxml.SxmlNode|str, foot_notes: dict):
    def get_id(old: str, new: str) -> str:
        return old if old in ['i', 'b', 'em', 'strong', 'article', 'section', 'p'] else new

    if type(n) is not sxml.SxmlNode:
        return

    def match(ty: str, m: str):
        if m in ty:
            zz = []
            for q in ty.split(' '):
                if q.startswith(m):
                    q = ''
                zz.append(q)
            ty = ' '.join(zz)
            ty = ty.strip()
            return True, ty
        return False, ty

    def set_id_on_match(ty: str, m: str, id: str = ''):
        id = id if id else m
        f, ty = match(ty, m)
        if f:
            n.id = id
        return ty

    __rewrite_note(n, foot_notes)
    n.id = 'drop' if n.id == 'figure' else n.id
    if 'type' in n.attrs:
        ty = n.attrs['type']
        ty = set_id_on_match(ty, 'se:name', get_id(n.id, 'span'))
        ty = set_id_on_match(ty, 'se:diary', get_id(n.id, 'span'))
        ty = set_id_on_match(ty, 'se:image', get_id(n.id, 'span'))
        ty = set_id_on_match(ty, 'se:letter', get_id(n.id, 'span'))
        ty = set_id_on_match(ty, 'label', get_id(n.id, 'span'))
        ty = set_id_on_match(ty, 'ordinal', get_id(n.id, 'span'))
        ty = set_id_on_match(ty, 'z3998:roman', get_id(n.id, 'span'))
        ty = set_id_on_match(ty, 'z3998:place', get_id(n.id, 'span'))
        ty = set_id_on_match(ty, 'z3998:nationality', get_id(n.id, 'span'))
        ty = set_id_on_match(ty, 'z3998:taxonomy', get_id(n.id, 'span'))
        ty = set_id_on_match(ty, 'z3998:morpheme', get_id(n.id, 'span'))
        ty = set_id_on_match(ty, 'z3998:phoneme', get_id(n.id, 'span'))
        ty = set_id_on_match(ty, 'z3998:event', get_id(n.id, 'span'))
        ty = set_id_on_match(ty, 'z3998:diary', get_id(n.id, 'span'))
        ty = set_id_on_match(ty, 'z3998:sender', get_id(n.id, 'span'))
        ty = set_id_on_match(ty, 'z3998:postscript', get_id(n.id, 'span'))
        ty = set_id_on_match(ty, 'z3998:signature', get_id(n.id, 'span'))
        ty = set_id_on_match(ty, 'z3998:salutation', get_id(n.id, 'span'))
        ty = set_id_on_match(ty, 'z3998:valediction', get_id(n.id, 'span'))
        ty = set_id_on_match(ty, 'z3998:recipient', get_id(n.id, 'span'))
        ty = set_id_on_match(ty, 'z3998:given-name', get_id(n.id, 'span'))
        ty = set_id_on_match(ty, 'title')
        ty = set_id_on_match(ty, 'dedication')
        ty = set_id_on_match(ty, 'z3998:introductory-note', 'introduction')
        ty = set_id_on_match(ty, 'z3998:dramatis-personae', 'dramatis-personae')
        ty = set_id_on_match(ty, 'z3998:stage-direction', 'stage-direction')
        ty = set_id_on_match(ty, 'z3998:drama', 'drama')
        ty = set_id_on_match(ty, 'z3998:scene', 'scene')
        ty = set_id_on_match(ty, 'z3998:persona', 'persona')
        ty = set_id_on_match(ty, 'z3998:verse', 'verse')
        ty = set_id_on_match(ty, 'z3998:song', 'song')
        ty = set_id_on_match(ty, 'z3998:poem', 'poem')
        ty = set_id_on_match(ty, 'z3998:letter', 'letter')
        ty = set_id_on_match(ty, 'z3998:grapheme', n.id)
        ty = set_id_on_match(ty, 'z3998:non-fiction', n.id)
        ty = set_id_on_match(ty, 'z3998:subchapter', n.id)
        ty = set_id_on_match(ty, 'chapter')
        ty = set_id_on_match(ty, 'epigraph')
        ty = set_id_on_match(ty, 'fulltitle', 'drop')

        ty = ty.strip()
        n.attrs['type'] = ty
        if not ty:
            n.attrs.pop('type')

    if n.id == 'nop' and 'id' in n.attrs:
        n.attrs.pop('id')
    if 'lang' in n.attrs:
        if len(n.attrs) == 1 and n.id in ['span', 'i', 'b', 'em', 'strong', 'nop']:
            n.id = 'i'
            n.attrs.pop('lang')
    if 'datetime' in n.attrs:
        n.attrs.pop('datetime')

    if 'class' in n.attrs:
        cls = n.attrs['class']
        for c in ['continued', 'i1', 'i2', 'i3', 'telegram', 'advertisement', 'supplemental', 'inscription', 'ciphertext', 'card', 'editorial', 'elision']:
            cls = cls.replace(c, '')
            cls = cls.strip()
            n.attrs['class'] = cls
        if not cls:
            n.attrs.pop('class')

    if 'id' in n.attrs:
        if n.id in ['chapter', 'section', 'letter', 'scene', 'drama']:
            n.attrs.pop('id')
    for x in n.xs:
        __traverse_node(x, foot_notes)

    drop = [x for x in n.list_nodes() if x.id == 'drop']
    for x in drop:
        n.xs.remove(x)

def __build_section_meta(n: sxml.SxmlNode, meta: SectionMeta, foot_notes: dict):
    # print('=======================================================')
    # print(meta.label)
    # print(meta.ordinal)
    # print(meta.title)
    # print(meta.subtitle)
    # print(meta.bridgehead)
    # print('===========')
    title_fn = ''
    if meta.title_notes:
        for y in meta.title_notes:
            __translate_note(y, foot_notes)
        title_fn = ''.join([sxml.to_xml(y) for y in meta.title_notes])
        title_fn = f'<title-notes>{title_fn}</title-notes>'
        qq = sxml.from_xml(title_fn)
        __traverse_node(qq, {})
        title_fn = sxml.to_xml(qq)

    if meta.label or meta.ordinal:
        meta.title = meta.title if meta.title else sxml.parse('(title)')

        if meta.label: meta.title.attrs['label'] = meta.label.value()
        if meta.ordinal: meta.title.attrs['n'] = meta.ordinal.value()
    if meta.title:
        meta.title.id = 'title'
    if meta.subtitle:
        meta.subtitle.id = 'subtitle'
    if meta.bridgehead:
        meta.bridgehead.id = 'bridgehead'

    title = sxml.to_xml(meta.title) if meta.title else ''
    subtitle = sxml.to_xml(meta.subtitle) if meta.subtitle else ''
    bridgehead = sxml.to_xml(meta.bridgehead) if meta.bridgehead else ''

    xs = ''
    xs += title
    if meta.subtitle: xs += subtitle
    if meta.bridgehead: xs += bridgehead
    xs += title_fn
    if xs:
        xs = '<meta>'+xs+'</meta>'
        meta_n = sxml.from_xml(xs)
        __traverse_node(meta_n, foot_notes)
        n.xs.insert(0, meta_n)
    else:
        # possible with dedication and other pages
        match n.attrs['type']:
            case 'dedication': title, pseudo = 'Dedication', True
            case 'epigraph': title, pseudo = 'Epigraph', True
            case 'prologue': title, pseudo = 'Prologue', False
            case 'epilogue': title, pseudo = 'Epilogue', False
            case 'chapter': title, pseudo = '', True
            case 'z3998:subchapter': title, pseudo = '', True
            case 'z3998:scene': title, pseudo = '', True
            case 'z3998:drama': title, pseudo = '', True
            case 'z3998:postscript': title, pseudo = '', True
            case 'z3998:diary-entry': title, pseudo = '', True
            case _: raise Exception(f'Unknown type `{n.attrs["type"]}`')

        if n.id == 'section':
            meta_n = None
        else:
            _pseudo = ' pseudo="true"' if pseudo else ''
            xs = f'<meta><title{_pseudo}>{title}</title></meta>'
            meta_n = sxml.from_xml(xs)
            __traverse_node(meta_n, foot_notes)
            n.xs.insert(0, meta_n)
        meta.title = meta_n


def collect_notes(n: sxml.SxmlNode):
    ys = [x for x in n.list_nodes() if x.attrs.get('type') == 'noteref']
    for x in ys:
        n.xs.remove(x)
    return ys

def __collect(n: sxml.SxmlNode, types: str, foot_notes: dict):
    # only collect within header/hgroup without attrs
    # all other elements need type attr before we descend

    # delete node once we collect it
    # also delete empty parent nodes

    drop = []
    collected = []
    for x in n.list_nodes():
        if 'type' in x.attrs and not x.attrs['type'].strip():
            x.attrs.pop('type')
        if 'type' in x.attrs:
            xs = x.attrs['type'].strip().split(' ')
            for type in types.split(' '):
                if type in xs:
                    xs.remove(type)
            if xs:
                x.attrs['type'] = ' '.join(xs)
            else:
                x.attrs.pop('type')
            if not x.attrs or ('lang' in x.attrs and len(x.attrs) == 1):
                drop.append(x)
                collected.append(x)
        if x.id in ['header', 'hgroup', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'] or (x.id in ['p'] and 'type' in x.attrs):
            q = __collect(x, types, foot_notes)
            if q:
                collected.extend(q)

    for x in drop:
        n.xs.remove(x)
    __clear_empty_nodes(n)
    return collected

def __collect_sections(n: sxml.SxmlNode, foot_notes: dict):
    for x in n.list_nodes():
        if x.id in ['section']:
            __section_meta(x, foot_notes)

def __clear_empty_nodes(n: sxml.SxmlNode):
    drop = []
    for x in n.list_nodes():
        if not x.xs and not x.attrs and x.id in ['hgroup', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'span']:
            drop.append(x)
        __clear_empty_nodes(x)

    for x in drop:
        n.xs.remove(x)

def __section_meta(n: sxml.SxmlNode, footnotes: dict):
    # descend tree and collect the required info
    xs = __collect(n, 'label', footnotes)
    assert len(xs) <= 1
    label = xs[0] if xs else None

    xs = __collect(n, 'ordinal z3998:roman', footnotes)
    assert len(xs) <= 1
    ordinal = xs[0] if xs else None

    xs = __collect(n, 'title', footnotes)
    assert len(xs) <= 1
    title = xs[0] if xs else None
    title_notes = collect_notes(title) if title else []

    xs = __collect(n, 'subtitle', footnotes)
    if len(xs) <= 1:
        subtitle = xs[0] if xs else None
    else:
        subtitle = sxml.from_xml('<div>'+(''.join([sxml.to_xml(x) for x in xs]))+'</div>')

    xs = __collect(n, 'bridgehead', footnotes)
    assert len(xs) <= 1
    bridgehead = xs[0] if xs else None

    # if you encounter section, start a new descent
    __collect_sections(n, footnotes)

    meta = SectionMeta(label, ordinal, title, subtitle, bridgehead, title_notes)
    __build_section_meta(n, meta, footnotes)
    return meta

def __parse_chapter(ses: SeSource, book: SeBook, pc: SeChapter|None, chapter: SeChapter):
    html = chapter.load()
    body = html.first_('body')
    assert len(body.xs) == 1
    matter = body.node(0)
    matter.id = 'chapter'
    chapter.meta = __section_meta(matter, book.footnotes)
    matter.attrs = {}

    meta = matter.xs.pop(0)
    assert isinstance(meta, sxml.SxmlNode) and meta.id == 'meta'

    __traverse_node(matter, book.footnotes)
    xml = f'<document uuid="">{sxml.to_xml(meta).replace('<meta>', '<meta>'+__source_info(ses.work))}{sxml.to_xml(matter)}</document>'

    slug_title = __title_for_slug(pc, chapter)
    title_node = meta.first('title')
    title = title_node.value_rec()
    number = title_node.attrs.get('n', '')
    label = title_node.attrs.get('label', '')

    c_url = make_slug(slug_title) + '.xml'
    df = f'{ses.base_out}/{c_url}'
    chapter.xml = xml
    chapter.write(ses, df)
    return RefEntry(c_url, label, number, title)

def __title_for_slug(pc: SeChapter|None, c: SeChapter):
    def to_str(x: sxml.SxmlNode|None) -> str:
        return x.value_rec() if x else ''

    assert c.meta
    title = to_str(c.meta.title)
    if not title:
        title += to_str(c.meta.subtitle)
        if not title:
            title += to_str(c.meta.bridgehead)
            if not title:
                label = to_str(c.meta.label)
                ordinal = to_str(c.meta.ordinal)
                if label:
                    title += label
                    title += ' '
                    title += ordinal
                else:
                    if pc and pc.meta:
                        yy = to_str(pc.meta.ordinal)
                        if text.is_roman(yy):
                            title += yy
                            title += ' '
                    title += ordinal
    assert title != ''
    return title

def __source_info(work: str):
    url_part = '/'.join(work.split('_'))
    xs = ''
    xs += '<copyright>CC0/PD. No rights reserved</copyright>'
    xs += f'<source url="https://standardebooks.org/ebooks/{url_part}">Standard Ebooks</source>'
    return xs

def parse_book(ses: SeSource):
    def book_meta(xml: str):
        from mod.lib.text import between_inclusive
        title = sxml.from_xml(between_inclusive(xml, '<dc:title', '</dc:title>').replace('dc:', '')).value()
        author = sxml.from_xml(between_inclusive(xml, '<dc:creator', '</dc:creator>').replace('dc:', '')).value()
        return title, author

    def visit_chapters(n: sxml.SxmlNode, book: SeBook, pc: SeChapter|None):
        for li in n.list_nodes():
            a = li.first_('a')
            href = a.attrs['href']
            if '#' in href:
                continue
            ref = href.split('/')[-1]
            if ref in ['imprint.xhtml',
                        'colophon.xhtml',
                        'titlepage.xhtml',
                        'loi.xhtml',
                        'uncopyright.xhtml',
                        'endnotes.xhtml'
                        ]:
                continue

            c = SeChapter.from_file(ses, f'{ses.base}/{href}', a.value_rec())
            print('==' + c.title)
            if ref in ['halftitlepage.xhtml']:
                pass
            else:
                r = __parse_chapter(ses, book, pc, c)
                book.chapters.append(c)
                book.toc.append(r)
            z = li.first('ol')
            if z:
                visit_chapters(z, book, c)

    def handle_footnotes() -> FootNotes:
        footnotes = {}
        notes_file = f'{ses.base}/text/endnotes.xhtml'
        if ses.exists(notes_file):
            n = SeChapter.from_file(ses, notes_file, 'ENDNOTES').load()
            xs = []
            xs.extend(n.all('body/section/ol/li'))
            for x in xs:
                assert type(x) is sxml.SxmlNode
                nid = x.attrs['id'].split('-')[-1]
                footnotes[nid] = []
                for c in x.list_nodes():
                    __drop_node(c, 'type', 'backlink')
                    footnotes[nid].append(c)
        return footnotes


    print(f'parsing ---------------------------------- {ses.work}')

    # get title and author
    title, author = book_meta(ses.read_text(f'{ses.base}/content.opf'))
    book = SeBook(ses.work, title, author, [], handle_footnotes(), [])
    toc_file = SeChapter.from_file(ses, f'{ses.base}/toc.xhtml', 'TOC')
    visit_chapters(toc_file.load().first_('body/nav/ol'), book,None)

    toc = ''
    toc += '<toc>'
    for r in book.toc:
        nn = f' n="{r.n}"' if r.n else ''
        ll = f' label="{r.label}"' if r.label else ''
        toc += f'<ref url="{r.url}"{ll}{nn}>{r.title}</ref>'
    toc += '</toc>'

    x = '<document uuid="">'
    x += '<meta>'
    x += __source_info(ses.work)
    x += f'<title>{title}</title>'
    if author: x += f'<author>{author}</author>'
    x += '</meta>'
    x += toc
    x += '</document>'

    toc_file.xml = x
    toc_file.write(ses, f'{ses.base_out}/index.xml')

cwd = f'{env.CACHE_ROOT}/standard-ebooks'
def __download_master(work: str):
    fp = f'{cwd}/{work}.zip'
    fs.ensure_parent(fp)
    if fs.exists(fp):
        return
    print(f'downloading {work}')
    url = f'https://github.com/standardebooks/{work}/archive/refs/heads/master.zip'
    fs.exec(['wget', url, '--output-document', fp], cwd)
    fs.exec(['unzip', fp], cwd)

def process(file: str, debug: bool):
    WORKS = __get_works_list('standard-ebooks', file)
    for work in WORKS:
        __download_master(work)
        base = f'{cwd}/{work}-master/src/epub'
        base_out = __se_raw_base(work)
        ses = SeSource(base, base_out, work, fs.read_text, fs.write_text, fs.exists)
        parse_book(ses)
        project_uuids.set_project_doc_uuids(base_out)