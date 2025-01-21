import pprint
import re
from mod.lib import fs, mxml
from mod.lib.mxml import XmlNode
from mod.root.backend.importers.tp.book_generate import Pretty

def write_xml(fp: str, doc: XmlNode):
    try:
        xml = mxml.unparse(doc, Pretty).strip()
        xml = re.sub(r'\s*<br/>\s*', '<br/>', xml)
        fs.write_text(fp, xml)
    except Exception as e:
        pprint.pprint(doc)
        raise e

def get_uuids_for_work(fn: str) -> list:
    if not fs.exists(fn):
        return []
    uuids = [x for x in fs.read_text(fn).split('\n') if x.strip()]
    uuids.reverse()
    return uuids

def __get_doc_uuid(fp: str, ref: str):
    ids = f'{fp}/ids'
    if fs.exists(ids):
        for y in [x.split(' ') for x in fs.read_text(ids).splitlines()]:
            u, f = y
            if f == ref:
                return u
        raise Exception(f'Could not find {ref} in {ids}')
    else:
        from mod.lib import uuid
        return uuid.gen()

def __set_doc_uuid(fp: str, ref: str):
    file = f'{fp}/{ref}'
    doc = mxml.parse(fs.read_text(file), Pretty)
    doc.attrs['uuid'] = __get_doc_uuid(fp, ref)
    write_xml(file, doc)
    return doc

def set_project_doc_uuids(fp: str):
    def traverse(p: mxml.XmlNode, xs: list[str]):
        url = p.attrs.get('url', '')
        if url:
            doc = __set_doc_uuid(fp, url)
            xs.append(f'{doc.attrs['uuid']} {url}')
        else:
            for c in p.list_nodes():
                traverse(c, xs)

    xs = []
    doc = __set_doc_uuid(fp, 'index.xml')
    xs.append(f'{doc.attrs['uuid']} index.xml')
    traverse(doc.first_('toc'), xs)

    ids = f'{fp}/ids'
    fs.write_text(ids, '\n'.join(xs))
