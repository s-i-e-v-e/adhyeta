import pprint
import time

from mod.lib import sxml
from mod.lib.fs import list_dirs, list_files, File, read_text
from mod.lib.sqlite_db import Database
from mod.lib.sxml.parser import SxmlNode
from mod.lib.text import normalize, make_slug, to_json
from mod.root.backend.importers.traversal import sxml_validate_doc
from mod.root.backend.importers.traversal.sxml_count_words import count_words
from mod.root.data import doc, word

'''
document @title OPT @loc OPT @uuid REQUIRED
-   meta
    -   title
    -   author
    -   source @page @url @date @@ label
    -   copyright
    -   category @@ c1(br)c2(br)c3
    -   note
-   toc
    -   ref @url OPT URL @local OPT ID @@ label
-   matter 
'''


def __collect_metadata(doc: SxmlNode, meta: SxmlNode) -> dict:
    METADATA_NODES = [
        'title',
        'subtitle',
        'bridgehead',
        'source',
        'copyright',
        'category',
        'author',
        'note',
        'original',
    ]

    x = {}
    for label in METADATA_NODES:
        b = meta.first(label)
        if not b:
            if label == 'title':
                # get title from doc attrs
                x[label] = doc.attrs[label]
            continue
        x[label] = b.value_rec()
        if label == 'title':
            x['title_label'] = b.attrs.get('label', '')
            x['title_n'] = b.attrs.get('n', '')

        if label == 'source':
            x['source_page'] = b.attrs.get('page', '')
            x['source_url'] = b.attrs.get('url', '')
            x['source_date'] = b.attrs.get('date', '')

    x['__title'] = x['title']
    if not x['title']:
        # is empty
        x['__title'] = (x['title_label'] + ' ' + x['title_n']).strip()

    return x

def __import_file_into_db(db: Database, f: File, rel_parent: str):
    if not f.name.endswith(".sxml"):
        return
        #raise Exception(f"Expected an SXML file. Found {f.full_path}")
    sf = f.full_path
    print(f"Importing {f.full_path}")

    text = normalize(read_text(sf)).replace("--", "—").replace("-\n", "")
    n = sxml.parse(text)
    sxml_validate_doc.validate(n)
    uuid = n.attrs["uuid"]
    loc = n.attrs.get('loc', '')

    ys = []
    word_set, total_words = count_words(n)
    for x in word_set:
        w = word.save(db, x)
        ys.append((w.hash, w.word, x))


    metadata = __collect_metadata(n, n.first('meta'))
    metadata['unique_words'] = str(len(ys))
    metadata['total_words'] = str(total_words)
    metadata['original_loc'] = f"{rel_parent}/{f.name}".replace("//", "/")
    meta = to_json(metadata)

    title = metadata['__title']
    fn = "index.sxml" if f.name == "index.sxml" else f"{make_slug(title)}.sxml"
    loc = loc if loc else f"{rel_parent}/{fn}"
    loc = loc.replace("//", "/")

    d = doc.get_by_uuid(db, uuid)
    if d is None:
        print(f"Adding {loc}")
        d = doc.save(db, uuid, loc, title, text, meta, time.time_ns(), ys)
    else:
        if d.loc != loc:
            raise Exception(f"Duplicate UUID. Won: {d.loc} Lost:{loc}")
        if d.text != text:
            print(f"Updating {loc}")
            d = doc.save(db, uuid, loc, title, text, meta, time.time_ns(), ys)
    assert d

def import_files_into_db(db: Database, xs: list[File], prefix: str):
    for f in xs:
        rel_parent = f.parent
        f.full_path = f'{prefix}{f.full_path}'
        f.parent = f'{prefix}{f.parent}'
        __import_file_into_db(db, f, rel_parent)

def import_dir_into_db(db: Database, p: File, rel_parent: str):
    for f in list_dirs(p.full_path):
        import_dir_into_db(db, f, f"{rel_parent}/{f.name}")

    for f in list_files(p.full_path):
        __import_file_into_db(db, f, rel_parent)
