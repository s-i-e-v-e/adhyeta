'''
Take Standard E-books PD content and convert it into
markup usable for further processing
'''
import copy
import pprint
import re

from mod.config import env
from mod.lib import fs, mxml, text
from mod.lib.mxml import XmlNode
from mod.root.backend.importers.tp import __get_works_list, __se_raw_base, project_uuids
from mod.root.backend.importers.tp import book_generate
from mod.root.backend.importers.tp.book_generate import Pretty, ChapterMeta, BookMeta, TocEntry

'''
#######################################################
Clean up the source
#######################################################
'''


def __wipe(xml: str, x: str):
    return xml.replace(x, '')


def __replace(xml: str, strip_hrefs: bool) -> str:
    xml = text.between_inclusive_replace(xml, '<?xml', '?>\n', '')
    xml = text.between_inclusive_replace(xml, '<html', '>\n', '<html>\n')
    assert xml[0:6] == '<html>'
    xml = text.between_inclusive(xml, '<body', '</body>')

    xml = xml.replace('epub:type', 'type')
    xml = xml.replace('xml:lang', 'lang')

    # replace all the irrelevant z3998 references
    xml = __wipe(xml, 'se:short-story')
    xml = __wipe(xml, 'se:novella')
    xml = __wipe(xml, 'se:era')
    xml = __wipe(xml, 'se:compass')
    xml = __wipe(xml, 'se:name.legal-case')
    xml = __wipe(xml, 'se:name.vehicle.train')
    xml = __wipe(xml, 'se:name.vessel.boat')
    xml = __wipe(xml, 'se:name.vessel.ship')
    xml = __wipe(xml, 'se:name.visual-art.painting')
    xml = __wipe(xml, 'se:name.visual-art.sculpture')
    xml = __wipe(xml, 'se:name.music.opera')
    xml = __wipe(xml, 'se:name.music.song')
    xml = __wipe(xml, 'se:name.music')
    xml = __wipe(xml, 'se:name.publication.book')
    xml = __wipe(xml, 'se:name.publication.essay')
    xml = __wipe(xml, 'se:name.publication.journal')
    xml = __wipe(xml, 'se:name.publication.magazine')
    xml = __wipe(xml, 'se:name.publication.newspaper')
    xml = __wipe(xml, 'se:name.publication.pamphlet')
    xml = __wipe(xml, 'se:name.publication.paper')
    xml = __wipe(xml, 'se:name.publication.play')
    xml = __wipe(xml, 'se:name.publication.poem')
    xml = __wipe(xml, 'se:name.publication.short-story')
    xml = __wipe(xml, 'se:name.publication')
    xml = __wipe(xml, 'se:image.color-depth.black-on-transparent')

    xml = __wipe(xml, 'z3998:fiction')
    xml = __wipe(xml, 'z3998:non-fiction')
    xml = __wipe(xml, 'z3998:subchapter')
    xml = __wipe(xml, 'z3998:name-title')
    xml = __wipe(xml, 'z3998:personal-name')
    xml = __wipe(xml, 'z3998:given-name')
    xml = __wipe(xml, 'z3998:surname')
    xml = __wipe(xml, 'z3998:place')
    xml = __wipe(xml, 'z3998:nationality')
    xml = __wipe(xml, 'z3998:event')
    xml = __wipe(xml, 'z3998:initialism')
    xml = __wipe(xml, 'z3998:grapheme')
    xml = __wipe(xml, 'z3998:morpheme')
    xml = __wipe(xml, 'z3998:phoneme')
    xml = __wipe(xml, 'z3998:word')
    xml = __wipe(xml, 'z3998:taxonomy')
    xml = __wipe(xml, 'z3998:acronym')
    xml = __wipe(xml, 'z3998:organization')
    xml = __wipe(xml, 'z3998:translator')
    xml = __wipe(xml, 'z3998:illustration')
    xml = __wipe(xml, 'z3998:roman')

    # need to handle this type in code
    xml = xml.replace('z3998:frontispiece', 'frontispiece')
    xml = xml.replace('z3998:introductory-note', 'intro')
    xml = xml.replace('z3998:postscript', 'postscript')  # end of letter/article etc
    xml = xml.replace('z3998:verse', 'verse')
    xml = xml.replace('z3998:poem', 'poem')
    xml = xml.replace('z3998:song', 'song')
    xml = xml.replace('z3998:hymn', 'hymn')

    xml = xml.replace('z3998:dramatis-personae', 'd-personae')
    xml = xml.replace('z3998:drama', 'drama')
    xml = xml.replace('z3998:scene', 'd-scene')
    xml = xml.replace('z3998:persona', 'd-persona')
    xml = xml.replace('z3998:stage-direction', 'd-stage-direction')

    xml = xml.replace('z3998:diary-entry', 'd-entry')
    xml = xml.replace('z3998:diary', 'diary')
    xml = xml.replace('se:diary.dateline', 'd-date')

    xml = xml.replace('z3998:letter', 'letter')
    xml = xml.replace('z3998:recipient', 'l-recipient')
    xml = xml.replace('z3998:salutation', 'l-salutation')
    xml = xml.replace('z3998:valediction', 'l-valediction')
    xml = xml.replace('z3998:signature', 'l-signature')
    xml = xml.replace('z3998:sender', 'l-sender')
    xml = xml.replace('z3998:subject', 'l-subject')
    xml = xml.replace('se:letter.dateline', 'l-date')

    xml = xml.replace('frontmatter', '')
    xml = xml.replace('bodymatter', '')
    xml = xml.replace('backmatter', '')
    xml = xml.replace('=" ', '="')
    xml = xml.replace('type=""', '')
    xml = re.sub(r'data-parent="[^"]*"', '', xml)
    if strip_hrefs:
        xml = re.sub(r'id="[^"]*"', '', xml)
        xml = re.sub(r'href="[^"]*"', '', xml)
    xml = re.sub(r'rel="[^"]*"', '', xml)
    xml = re.sub(r'datetime="[^"]*"', '', xml)
    xml = re.sub(r'lang="[^"]*"', '', xml)
    xml = re.sub(r'alt="[^"]*"', '', xml)
    xml = re.sub(r'class="[^"]*"', '', xml)

    xml = re.sub(r'<abbr *>([^<]+)</abbr>', r'\1', xml)
    return xml


def __debug(xml: str):
    unclean = []
    ma = re.findall(r'[ "](z3998:[^ "]*)', xml, flags=re.UNICODE)
    unclean.extend(ma)
    ma = re.findall(r'[ "](se:[^ "]*)', xml, flags=re.UNICODE)
    unclean.extend(ma)
    ma = re.findall(r'([a-z]+="[^"]*)', xml, flags=re.UNICODE)
    unclean.extend(ma)
    return unclean


'''
#######################################################
load and parse
#######################################################
'''

FootNotes = dict[str, list[mxml.XmlNode]]

def __translate_note(n: mxml.XmlNode, foot_notes: dict):
    if 'type' in n.attrs and n.attrs['type'] == 'noteref':
        assert n.id == 'a'
        n.id = 'fn'
        n.attrs.pop('href')
        n.attrs.pop('id')
        n.attrs.pop('type')
        n.attrs['n'] = n.value()
        n.xs = foot_notes[n.attrs['n']]
        pprint.pprint(n)

def __rewrite_note(n: mxml.XmlNode, foot_notes: dict):
    for x in n.list_nodes():
        __rewrite_note(x, foot_notes)
    __translate_note(n, foot_notes)

def __load_xhtml(parent: str, url_part: str, strip_hrefs: bool):
    path = '/'.join([parent, url_part])
    print('---------------parsing', path)
    if fs.exists(path):
        xml = fs.read_text(path)
        xml = __replace(xml, strip_hrefs)
        doc = mxml.parse(xml, Pretty)
        return doc
    else:
        return None

def __parse_chapter(n: mxml.XmlNode, footnotes: FootNotes):
    def a_in_b(xs: list[str], ys: list[str]) -> bool:
        return not not list(set(xs) & set(ys))

    def should_be_dropped(n: mxml.XmlNode):
        return not n.xs and n.id in ['hgroup', 'h1', 'h2', 'h3', 'p', 'span']

    def collect(n: mxml.XmlNode, cm: ChapterMeta):
        rm = []
        for c in n.list_nodes():
            a = collect(c, cm)
            if a:
                rm.append(a)
        for c in rm:
            n.xs.remove(c)
        for c in n.xs:
            if isinstance(c, str) and not c.strip():
                n.xs.remove(c)

        if 'type' not in n.attrs:
            if should_be_dropped(n):
                return n
            else:
                return None

        types = n.attrs['type'].strip().split(' ')
        if a_in_b(types, ['ordinal']):
            v = n.value()
            if text.is_roman(v):
                cm.ordinal = text.roman_to_int_str(v)
            else:
                match v.lower():
                    case 'the first':
                        cm.ordinal = str(1)
                    case 'the second':
                        cm.ordinal = str(2)
                    case 'the third':
                        cm.ordinal = str(3)
                    case 'the fourth':
                        cm.ordinal = str(4)
                    case 'the fifth':
                        cm.ordinal = str(5)
                    case _:
                        cm.ordinal = str(v)
            return n
        if a_in_b(types, ['label', 'ordinal', 'title', 'subtitle', 'bridgehead']):
            assert len(types) == 1
            type = types[0]
        else:
            type = types[0]
        if type in ['label']:
            cm.label = n.value()
            return n
        elif type in ['title']:
            if len(n.xs) == 1:
                try:
                    cm.title = n.value()
                except Exception as e:
                    pprint.pprint(n)
                    raise e
            else:
                cm.title = n
            return n
        elif type in ['bridgehead']:
            cm.bridgehead = n
            return n
        elif type in ['subtitle']:
            cm.subtitle.append(n)
            return n
        elif type in ['fulltitle']:
            cm.title = cm.title if cm.title else n.value()
            return n
        else:
            if should_be_dropped(n):
                return n
            else:
                return None

    # rewrite nodes
    # todo: is temporary. maybe keep the original html nodes
    def rewrite(n: mxml.XmlNode):
        if 'type' in n.attrs:
            xs = n.attrs['type'].split(' ')
            # if 'poem' in xs:
            #     xs.remove('poem')
            #     n.id = 'poem'
            if xs:
                n.attrs['type'] = ' '.join(xs)
            else:
                n.attrs.pop('type')
        if 'id' in n.attrs:
            n.attrs.pop('id')

        for c in n.list_nodes():
            rewrite(c)

    # recursively look for
    # optional label + ordinal
    # optional title
    # optional subtitle
    # optional bridgehead

    __rewrite_note(n, footnotes)

    x = n.first('header')
    x = x if x else n.first('hgroup')
    x = x if x else n.first('h2')
    x = x if x else n.first('h3')
    cm = ChapterMeta('', '', '', [], '', False, None)
    if x:
        a = collect(x, cm)
        if a:
            n.xs.remove(a)
    else:
        cm.pseudo = True
        cm.title = n.attrs['type'].upper()

    rewrite(n)
    if not n.xs:
        # lift to toc
        pass
    else:
        if 'type' in n.attrs:
            n.id = n.attrs.pop('type')
        cm.content = n
    #
    # __translate_note(cm.title, footnotes)
    # __translate_note(cm.subtitle, footnotes)
    # __translate_note(cm.bridgehead, footnotes)
    return cm

def __parse_toc(out_base: str, parent: str):
    def slug(prefix: str, label: str, n: str, title: XmlNode | str):
        try:
            if isinstance(title, str):
                value = title
            else:
                tt = copy.deepcopy(title)
                pprint.pprint(tt)
                for fn in tt.all('fn'):
                    tt.xs.remove(fn)
                value = tt.value_rec()
            return text.make_slug(value) + '.xml'
        except:
            value = prefix + '-' + label + '-' + n
            return text.make_slug(value) + '.xml'

    def book_meta(xml: str):
        from mod.lib.text import between_inclusive
        title = mxml.parse(between_inclusive(xml, '<dc:title', '</dc:title>').replace('dc:', '')).value()
        author = mxml.parse(between_inclusive(xml, '<dc:creator', '</dc:creator>').replace('dc:', '')).value()
        try:
            translator = mxml.parse(
                between_inclusive(xml, '<dc:contributor id="translator"', '</dc:contributor>').replace('dc:',
                                                                                                       '')).value()
        except:
            translator = ''

        work = parent.split('/')[-3].split('-master')[0]
        url_part = '/'.join(work.split('_'))

        url = f'https://standardebooks.org/ebooks/{url_part}'
        return BookMeta('CC0/PD. No rights reserved', url, 'Standard Ebooks', title, author, translator)

    def book_footnotes(doc: XmlNode|None) -> FootNotes:
        footnotes = {}
        if not doc:
            return footnotes

        xs = doc.all('section/ol/li')
        for x in xs:
            assert type(x) is mxml.XmlNode
            nid = x.attrs['id'].split('-')[-1]
            footnotes[nid] = []
            for c in x.list_nodes():
                c.drop_child_where('type', 'backlink')
                footnotes[nid].append(c)
        return footnotes

    def visit_chapters(n: mxml.XmlNode, footnotes: FootNotes, pr: str = ''):
        refs = []
        for li in n.list_nodes():
            a = li.first_('a')
            url = a.attrs['href']
            if '#' in url:
                continue
            if [x for x in ['titlepage.xhtml', 'imprint.xhtml', 'colophon.xhtml', 'loi.xhtml', 'uncopyright.xhtml',
                            'endnotes.xhtml'] if url.endswith('/'+x)]:
                continue

            c = __load_xhtml(parent, url, False)
            x = c.first('section') if c.first('section') else c.first('article')
            assert x is not None
            cm = __parse_chapter(x, footnotes)
            if cm.content:
                ref = TocEntry(cm, slug(pr, cm.label, cm.ordinal, cm.title), [])
            else:
                ref = TocEntry(cm, '', [])
            refs.append(ref)
            ol = li.first('ol')
            if ol:
                _refs = visit_chapters(ol, footnotes, f'{pr}-{cm.ordinal}')
                ref.xs = _refs
        return refs

    bm = book_meta(fs.read_text(parent + '/content.opf'))
    footnotes = book_footnotes(__load_xhtml(parent, 'text/endnotes.xhtml', False))
    n = __load_xhtml(parent, 'toc.xhtml', False)
    refs = visit_chapters(n.first_('nav/ol'), footnotes)
    book_generate.process(out_base, bm, refs)

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


def __process_work(xs: list[str]):
    for work in xs:
        __download_master(work)
        base = f'{cwd}/{work}-master/src/epub'
        base_out = __se_raw_base(work)
        __parse_toc(base_out, base)
        project_uuids.set_project_doc_uuids(base_out)


def process(file: str):
    xs = __get_works_list('standard-ebooks', file)
    __process_work(xs)
