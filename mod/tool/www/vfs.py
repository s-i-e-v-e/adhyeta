from dataclasses import dataclass
from mod.lib import sxml
from mod.lib.fs import list_files, list_dirs, read_text, File, stat
from mod.lib.sqlite_db import Database
from mod.lib.sxml.parser import SxmlNode
from mod.tool.www.db import db_insert, db_list_locations
from mod.lib.text import normalize, make_slug

VirtualFS = dict[str, list[str]]

@dataclass
class State:
    db: Database
    force: bool
    last_update_ns: int

def build_vfs(db: Database) -> VirtualFS:
    q = VirtualFS()

    def add_to_parent(loc: str):
        def add(p: str, c: str):
            if p != c:
                q[p].append(c)

        xs = loc.split("/")
        ys = []
        pp = ""
        for x in xs:
            ys.append(x)
            yy = "/".join(ys)
            if yy not in q:
                q[yy] = []
            add(pp, yy)
            pp = yy

        ys = xs[0:-1]
        yy = "/".join(ys)
        add(yy, loc)

    for [x] in db_list_locations(db):
        add_to_parent(x)

    for k in q.keys():
        xs = list(set(q[k]))

        for f in xs:
            if f.endswith("/index.sxml"):
                xs.remove(f)
                xs.insert(0, f)
                break
        q[k] = xs
    return q

def get_document_title(n: SxmlNode):
    title = sxml.sxml_node_as_str(n, "/document/title")
    title = title if title else n.attrs["title"]
    return title

def load_file_into_db(state: State, f: File):
    if not f.name.endswith(".sxml"):
        raise Exception(f"Expected an SXML file. Found {f.full_path}")
    sf = f.full_path

    skip = not(f.name == "index.sxml" or state.force or stat(sf).st_mtime_ns > state.last_update_ns)

    text = normalize(read_text(sf)).replace("--", "—").replace("-\n", "")
    n = sxml.parse(text)

    sxml.move_node_to_end(n, "/document/source")
    sxml.move_node_to_end(n, "/document/copyright")
    sxml.move_node_to(n, "/document/title", 0)

    title = get_document_title(n)

    loc = n.attrs["loc"]
    if loc.endswith(".sxml"):
        pass
    else:
        fn = "index.sxml" if f.name == "index.sxml" else f"{make_slug(title)}.sxml"
        loc = f"{loc}/{fn}"
        loc = loc.replace("//", "/")
    db_insert(state.db, loc, title, n, text, skip)


def load_files_into_db(state: State, p: File):
    for f in list_dirs(p.full_path):
        load_files_into_db(state, f)

    for f in list_files(p.full_path):
        load_file_into_db(state, f)
