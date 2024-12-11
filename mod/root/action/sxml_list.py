from mod.lib import sxml
from mod.lib.sqlite_db import Database
from mod.root.data import doc

def __generate_files_list(db: Database, parent: str):
    def get_files():
        dd = dict[str, str]()
        for d in doc.get_child_docs(db, parent):
            if d.loc.endswith("/index.sxml"):
                continue
            if d.title:
                dd[d.title] = d.loc
        return dict(sorted(dd.items()))

    fs = get_files()
    xs = []
    xs.append("(p")
    for title in fs:
        f = fs[title]
        ff = f.replace(".sxml", ".html")
        xs.append(f"""(lit (a @href "{ff}" {title}))""")
    xs.append(")")
    return sxml.sxml_parse("".join(xs))

def handle_list_pragma(db: Database, y: sxml.SxmlNode, floc: str):
    base_dir = sxml.get_str_node_val(y, "/document/sec/x-list")
    if base_dir:
        d = "/".join(floc.split("/")[0:-1])
        z = __generate_files_list(db, d)
        sxml.replace_node(y, "/document/sec/x-list", z)