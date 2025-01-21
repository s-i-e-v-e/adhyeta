'''
#######################################################
generate
#######################################################
'''
import dataclasses
from mod.lib import mxml, fs
from mod.root.backend.importers.tp import project_uuids


@dataclasses.dataclass
class BookMeta:
    copyright: str
    source_url: str
    source_value: str
    title: str
    author: str
    translator: str


@dataclasses.dataclass
class ChapterMeta:
    label: str
    ordinal: str
    title: mxml.XmlNode | str
    subtitle: list[mxml.XmlNode | str]
    bridgehead: mxml.XmlNode | str
    pseudo: bool
    content: mxml.XmlNode | None


@dataclasses.dataclass
class TocEntry:
    meta: ChapterMeta
    url: str
    xs: list['TocEntry']

Pretty = mxml.Prettifier.build('copyright source title author translator subtitle bridgehead ref p',
                               'document meta original toc matter chapter section blockquote poem')

def __set_source_info(bm: BookMeta, doc: mxml.XmlNode):
    doc.first_('meta/copyright').xs.append(bm.copyright)

    source = doc.first_('meta/source')
    source.attrs['url'] = bm.source_url
    source.xs.append(bm.source_value)

    doc.first_('meta/title').xs.append(bm.title)
    doc.first_('meta/author').xs.append(bm.author)
    doc.first_('meta/translator').xs.append(bm.translator)

def __generate_chapter(out_base: str, bm: BookMeta, c: ChapterMeta, url: str):
    print(f'Generating Chapter {url}')
    doc = mxml.parse(
        '<document uuid=""><meta><copyright/><source/><title/><author/><translator/><subtitle/><bridgehead/></meta></document>')
    assert c.content

    __set_source_info(bm, doc)

    title = doc.first_('meta/title')
    title.attrs['b'] = title.xs.pop()
    title.attrs['l'] = c.label
    title.attrs['n'] = c.ordinal
    title.xs.append(c.title)
    doc.first_('meta/subtitle').xs.extend(c.subtitle)
    doc.first_('meta/bridgehead').xs.append(c.bridgehead)
    doc.xs.append(c.content)
    project_uuids.write_xml(f'{out_base}/{url}', doc)

def __generate_index(out_base: str, bm: BookMeta, xs: list[mxml.XmlNode]):
    doc = mxml.parse(
        '<document uuid=""><meta><copyright/><source/><title/><author/><translator/></meta><toc/></document>')

    __set_source_info(bm, doc)
    doc.first_('toc').xs.extend(xs)
    project_uuids.write_xml(f'{out_base}/index.xml', doc)


def process(out_base: str, bm: BookMeta, refs: list[TocEntry]):
    def visit_ref(refs: list[TocEntry]) -> list[mxml.XmlNode]:
        xs = []
        for r in refs:
            rn = mxml.parse('<ref/>')
            rn.attrs['url'] = r.url
            rn.attrs['l'] = r.meta.label
            rn.attrs['n'] = r.meta.ordinal
            rn.xs.append(r.meta.title)

            xs.append(rn)
            if r.xs:
                xs.extend(visit_ref(r.xs))
            else:
                __generate_chapter(out_base, bm, r.meta, r.url)

        return xs
    xs = visit_ref(refs)
    __generate_index(out_base, bm, xs)