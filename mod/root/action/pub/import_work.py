from mod.lib import sxml
from mod.lib.fs import list_dirs, list_files, File, stat, read_text
from mod.lib.text import normalize, make_slug
from mod.root.action.pub import State, get_document_title
from mod.root.data import word, doc

def __import_file_into_db(state: State, f: File):
    if not f.name.endswith(".sxml"):
        raise Exception(f"Expected an SXML file. Found {f.full_path}")
    sf = f.full_path

    text = normalize(read_text(sf)).replace("--", "—").replace("-\n", "")
    n = sxml.parse(text)
    title = get_document_title(n)
    update_time_ns = stat(sf).st_mtime_ns
    loc = n.attrs["loc"]
    if loc.endswith(".sxml"):
        pass
    else:
        fn = "index.sxml" if f.name == "index.sxml" else f"{make_slug(title)}.sxml"
        loc = f"{loc}/{fn}"
        loc = loc.replace("//", "/")

    doc.save(state.db, loc, title, text, update_time_ns)

def import_files_into_db(state: State, p: File):
    for f in list_dirs(p.full_path):
        import_files_into_db(state, f)

    for f in list_files(p.full_path):
        __import_file_into_db(state, f)