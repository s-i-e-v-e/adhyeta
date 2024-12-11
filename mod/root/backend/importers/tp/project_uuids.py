from mod.lib import fs, sxml
from mod.root.backend.importers.tp import __se_raw_base, __gut_raw_base

def get_uuids_for_work(fn: str) -> list:
    if not fs.exists(fn):
        return []
    uuids = [x for x in fs.read_text(fn).split('\n') if x.strip()]
    uuids.reverse()
    return uuids

def set_project_doc_uuids(fp: str):
    def get_uuid(ref: str):
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

    def set_doc_uuid(ref: str):
        file = f'{fp}/{ref}'
        doc = sxml.from_xml(fs.read_text(file))
        doc.attrs['uuid'] = get_uuid(ref)
        fs.write_text(file, sxml.to_xml(doc))
        return doc

    doc = set_doc_uuid('index.xml')
    for ref in doc.children_of(1):
        url = ref.attrs['url']
        set_doc_uuid(url)
    update_dir(fp)

def update_dir(fp: str):
    for f in fs.list_dirs(fp):
        update_dir(f.full_path)

    xs = []
    file = f'{fp}/index.xml'
    if not fs.exists(file):
        return
    doc = sxml.from_xml(fs.read_text(file))
    xs.append(f'{doc.attrs['uuid']} index.xml')
    for ref in doc.children_of(1):
        url = ref.attrs['url']
        file = f'{fp}/{url}'
        doc = sxml.from_xml(fs.read_text(file))
        xs.append(f'{doc.attrs['uuid']} {url}')
    ids = f'{fp}/ids'
    fs.write_text(ids, '\n'.join(xs))

def update():
    update_dir(__se_raw_base())
    update_dir(__gut_raw_base())