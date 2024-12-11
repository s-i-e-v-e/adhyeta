from mod.lib import sxml
from mod.lib.sqlite_db import Database
from mod.root.data import doc

def __generate_files_list(fs: dict[str, str]) -> sxml.SxmlNode:
    xs = []
    xs.append("(p")
    for title in fs:
        f = fs[title]
        xs.append(f"""(lit (a @href "{f}" {title}))""")
    xs.append(")")
    return sxml.parse("".join(xs))


def collect_direct_child_dirs(parent: str, xs: list[str]):
    zs = []
    for x in xs:
        yy = x.replace(parent, '')
        ys = yy.split('/')
        if len(ys) == 3 and ys[-1] == 'index.sxml':
            zs.append(x)
    return zs

def get_files(db: Database, parent: str, dirs_only: bool):
    dd = dict[str, str]()
    xs = doc.get_child_docs(db, parent)
    if dirs_only:
        ys = collect_direct_child_dirs(parent, [x.loc for x in xs])
        xs = [x for x in xs if x.loc in [y for y in ys]]
    for d in xs:
        if not dirs_only and (d.loc.endswith("/index.sxml") or d.loc.endswith("/index2.sxml")):
            continue
        if d.title:
            dd[d.title] = d.loc
    return dict(sorted(dd.items()))

def handle_list_pragma(db: Database, y: sxml.SxmlNode, parent: str):
    _, p = sxml.filter_node(y, "/document/matter/x-list")
    if p:
        d = p.attrs.get('loc', '')
        d = d if d else parent
        fs = get_files(db, d, 'dirs' in p.attrs)
        z = __generate_files_list(fs)
        sxml.replace_node(y, "/document/matter/x-list", z)


def handle_table_pragma(db: Database, y: sxml.SxmlNode, parent: str):
    n = sxml.filter_node(y, "/document/matter/x-table")
    if not n:
        return
