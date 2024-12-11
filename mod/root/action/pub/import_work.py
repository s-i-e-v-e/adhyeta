import time

from mod.lib import sxml
from mod.lib.fs import list_dirs, list_files, File, read_text
from mod.lib.text import normalize, make_slug
from mod.root.action.pub import State, get_document_title
from mod.root.action.sxml_count_words import count_words
from mod.root.data import doc, word


def __import_file_into_db(state: State, f: File):
    if not f.name.endswith(".sxml"):
        raise Exception(f"Expected an SXML file. Found {f.full_path}")
    sf = f.full_path

    text = normalize(read_text(sf)).replace("--", "—").replace("-\n", "")
    n = sxml.parse(text)

    title = get_document_title(n)
    uuid = n.attrs["uuid"]
    loc = n.attrs["loc"]

    d =  doc.get_by_uuid(state.db, uuid)

    if loc.endswith(".sxml"):
        # file already has specific name
        pass
    else:
        fn = "index.sxml" if f.name == "index.sxml" else f"{make_slug(title)}.sxml"
        loc = f"{loc}/{fn}"
        loc = loc.replace("//", "/")

    ys = []
    for x in count_words(n):
        w = word.save(state.db, x)
        ys.append(w.id)

    if d is None:
        print(f"Adding {loc}")
        d = doc.save(state.db, uuid, loc, title, text, time.time_ns(), ys)
    else:
        if d.text != text:
            print(f"Updating {loc}")
            d = doc.save(state.db, uuid, loc, title, text, time.time_ns(), ys)
    assert d


def import_files_into_db(state: State, p: File):
    for f in list_dirs(p.full_path):
        import_files_into_db(state, f)

    for f in list_files(p.full_path):
        __import_file_into_db(state, f)