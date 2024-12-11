# take Standard E-books PD content and convert it into markup usable for further processing
from lxml import etree

from mod.config import env
from mod.lib import fs, sxml
from dataclasses import dataclass

from mod.lib.text import make_slug, roman_to_int
from mod.raw.deepseek import get_token_count
from mod.raw.work_uuids import get_uuids_for_work


@dataclass
class Chapter:
    uuid: str
    no: str
    title: str
    slug: str
    body: str

@dataclass
class Book:
    uuid: str
    title: str
    author: str
    chapters: list[Chapter]

WORKS = [
    # '0000-test-book',
    # 'o-henry_short-fiction',
    # 'oscar-wilde_an-ideal-husband',
    # 'h-g-wells_short-fiction',
    # 'h-g-wells_the-invisible-man',
    # 'anna-sewell_black-beauty',

    # 'edgar-allan-poe_short-fiction',
    # 'h-p-lovecraft_short-fiction',
    # 'beatrix-potter_short-fiction',
    # 'anthony-trollope_short-fiction',
    # 'm-r-james_short-fiction',
    # 'robert-e-howard_short-fiction',
    # 'herman-melville_short-fiction',
]

WORKS = [x for x in fs.read_text(f'{env.RAW_ROOT}/standard-ebooks/work.list').splitlines() if not x.startswith('#')]
cwd = '/tmp/standard-ebooks'
def __download_master(work: str):
    zip_fn = f'{work}.zip'
    fs.ensure_parent(f'{cwd}/{zip_fn}')
    if fs.exists(f'{cwd}/{zip_fn}'):
        return
    url = f'https://github.com/standardebooks/{work}/archive/refs/heads/master.zip'
    fs.exec(['wget', url, '--output-document', zip_fn], cwd)
    fs.exec(['unzip', zip_fn], cwd)

def __as_xml(f: str):
    def replace_epub_types(text, replacement=""):
        import re
        text = re.sub(r'z3998:author', 'author', text)
        text = re.sub(r'se:[a-zA-Z-.]+', replacement, text)
        text = re.sub(r'\s*z3998:[a-zA-Z-]+\s*', replacement, text)
        text = re.sub(r'\s*type=""', replacement, text)
        text = re.sub(r'\s*class=".*"', replacement, text)
        text = (text.replace('<span>', '<em>')
              .replace('</span>', '</em>')
              .replace('<abbr>', '')
              .replace('</abbr>', ''))
        return text
    xx = '\n'.join([x.strip() for x in fs.read_text(f).splitlines()])
    xx = (xx
          .replace('<?xml version="1.0" encoding="utf-8"?>', '')
          .replace('xmlns="http://www.w3.org/1999/xhtml"', '')
          .replace('epub:type', 'type')
          )
    xx = replace_epub_types(xx)
    chapter_no = '<h2 type="ordinal">'
    if chapter_no in xx:
        xx = xx.replace(chapter_no, '<chapter-no>')
        xx = xx.replace('</h2>', '</chapter-no>')


    idx_a = xx.index('<body')
    idx_b = xx.index('</body>')
    xx = xx[idx_a:idx_b+7]
    xx = xx.strip()
    n = etree.fromstring(xx)

    # validate
    for y in n.iter():
        if y.tag not in ['body', 'p', 'article', 'section', 'nav', 'h1', 'h2', 'ol', 'li', 'a', 'b', 'img', 'hr', 'br', 'blockquote', 'em', 'i', 'chapter-no', 'header', 'footer', 'hgroup']:
            print(y.text)
            raise Exception("error: "+y.tag)
    return n

@dataclass
class State:
    x: dict[str, str]
    xs: list[str]

def __traverse_node(n: etree.ElementBase, state: State):
    if 'title' == n.attrib.get('type', ''):
        state.x['title'] = n.text
    elif 'author' == n.attrib.get('type', ''):
        state.x['author'] = n.text
    elif 'chapter-no' == n.tag:
        state.x['chapter-no'] = n.text
    else:
        text = ''
        tag = n.tag
        skip_tag = False
        if tag == 'h1':
            tag = 'title'
        if tag == 'h2':
            tag = 'title'
        if tag == 'abbr':
            skip_tag = True
        if n.attrib.get('type', '') == 'dedication':
            tag = 'dedication'
        if not skip_tag:
            text += '('
            text += tag
        if tag not in ('br', 'hr'):
            text += ' '
            text += n.text or ""  # Get the text of the current node
        state.xs.append(text)
        for x in n:
            __traverse_node(x, state)

        text = ''
        if not skip_tag:
            text += ')'
        text += n.tail or ""  # Add tail text (text after the node)
        state.xs.append(text)

def __parse_title(n: etree.ElementBase):
    xs = n.xpath('//section[@id="titlepage"]')
    state = State({}, [])
    __traverse_node(xs[0], state)

    return state.x['title'], state.x['author']

def __parse_chapter(n: etree.ElementBase, uuid: str):
    xs = n.xpath('//article')
    if not len(xs):
        xs = n.xpath('//section')
    if not len(xs):
        raise Exception(f'no articles/chapters found')

    state = State({}, [])
    __traverse_node(xs[0], state)

    no = state.x.get('chapter-no', '')
    title = state.x['title']
    slug = make_slug(title)
    text = ''.join(state.xs)
    text = text.replace('(hgroup \n)\n', '')
    text = text.replace(' \n', '\n')
    text = text.strip()
    return Chapter(uuid, no, title, slug, text)

def __parse(work: str, uuids: list[str]):
    book = Book(uuids.pop(), '', '', [])

    base = f'{cwd}/{work}-master/src/epub'
    root = __as_xml(f'{base}/toc.xhtml')
    nav_ol = root.xpath('//nav[@id="toc"]//a')

    for x in nav_ol:
        href = x.attrib['href']
        fp = f'{base}/{href}'
        fn = href.split("/")[-1]
        if fn in  ['imprint.xhtml', 'colophon.xhtml', 'uncopyright.xhtml']:
            continue

        if fn == 'titlepage.xhtml':
            book.title, book.author = __parse_title(__as_xml(fp))
            continue
        print(href)
        book.chapters.append(__parse_chapter(__as_xml(fp), uuids.pop()))

    print(book.title, book.author)
    return book


def __write_index(dir: str, x: Book):
    xs = f"""
(document @uuid "{x.uuid}"
(title {x.title})
(author {x.author})
(matter
(x-list)
))""".strip()
    fs.write_text(f'{dir}/index.sxml', xs)

def __write_chapter(dir: str, x: Chapter, source_url: str):
    no = f'{str(roman_to_int(x.no)).zfill(2)}: ' if x.no else ''
    token_count = get_token_count(x.body)
    xs = f"""
(document @uuid "{x.uuid}" @tokens {token_count}
(copyright CC0. No rights reserved)
(source @url "{source_url}" Standard Ebooks)
(title {no}{x.title})
(note कृत्रिमबुद्ध्या कृतं भाषान्तरं इदं)
(matter
{x.body}
))""".strip()+'\n'
    print(f'{x.no}: {x.title} [{token_count}]')
    fs.write_text(f'{dir}/{x.slug}.sxml', xs)

SE_RAW_DIR =  f'{env.RAW_ROOT}/standard-ebooks'
def process():
    for work in WORKS:
        print(f'## {work} ##')
        __download_master(work)
        uuids = get_uuids_for_work(work)
        if not uuids:
            print(f'no uuids for {work}. skipping')
            continue
        b = __parse(work, uuids)
        slug_a = make_slug(b.author)
        slug_t = make_slug(b.title)
        dir = f"{SE_RAW_DIR}/{slug_a}/{slug_t}"
        __write_index(dir, b)
        source_url = f'https://standardebooks.org/ebooks/{slug_a}/{slug_t}'
        for x in b.chapters:
            __write_chapter(dir, x, source_url)