from mod.lib import sxml
from mod.lib import fs
from mod.root.action.sxml_publish_html import sxml_to_html, sxml_to_str
from mod.root.action.sxml_recognize_words import recognize_words
from mod.root.data import doc, word
from mod.root.action.pub import VirtualFS, State

TEMPLATE_HTML = sxml_to_str(sxml.parse(fs.read_text("./static/www.template.sxml")))

def generate_files_list(state: State, parent: str):
    def get_files():
        dd = dict[str, str]()
        for d in doc.get_child_docs(state.db, parent):
            if d.loc.endswith("/index.sxml"):
                continue
            if d.title:
                dd[d.title] = d.loc
        return dict(sorted(dd.items()))

    fs = get_files()
    xs = []
    xs.append("(ul")
    for title in fs:
        f = fs[title]
        ff = f.replace(".sxml", ".html")
        xs.append(f"""(li (a @href "{ff}" {title}))""")
    xs.append(")")
    return sxml.sxml_parse("".join(xs))

def handle_list_pragma(state: State, y: sxml.SxmlNode, floc: str):
    base_dir = sxml.get_str_node_val(y, "/document/sec/x-list")
    if base_dir:
        d = "/".join(floc.split("/")[0:-1])
        z = generate_files_list(state, d)
        sxml.replace_node(y, "/document/sec/x-list", z)

def handle_word_count(state: State, n: sxml.SxmlNode):
    unique_words = word.count_by_doc(state.db, n.attrs["uuid"])
    if sxml.node_exists(n, "/document/sec"):
        insert_at = "/document/category" if sxml.sxml_node_exists(n, "/document/category") else "/document/note" if sxml.sxml_node_exists(n, "/document/note") else "/document/author" if sxml.sxml_node_exists(n, "/document/author") else "/document/title"
        sxml.insert_node(n, insert_at, sxml.parse(f"(meta (p Unique Words: {unique_words}))"), 1)

def __to_html(state: State, y: sxml.SxmlNode, floc: str, title: str, bcx: str):
    handle_list_pragma(state, y, floc)
    handle_word_count(state, y)
    sxml.insert_node(y, "/document/meta", sxml.parse("(hr)"), 1)
    sxml.insert_node(y, "/document/sec", sxml.parse("(hr)"), 1)
    recognize_words(y, 0)
    html = sxml_to_str(y)
    return sxml_to_html(TEMPLATE_HTML, html, title, bcx)

BreadCrumbs = list[tuple[str, str]]

def generate_breadcrumb(bc: BreadCrumbs, current: str):
    if not len(bc):
        return ""
    html = """<nav id="crumbs">"""
    xs = []
    for uri, label in bc:
        if uri != current:
            xs.append(f"<a href='{uri}'>{label}</a>")
    html += " » ".join(xs)
    html += "</nav>"
    return html

def publish_files(state: State, vfs: VirtualFS, parent: str, this: str, bc: BreadCrumbs, dd: str, dd_base: str):
    if not this.endswith(".sxml"):
        bc = bc.copy()
        for x in vfs[this]:
            publish_files(state, vfs, this, x, bc, dd, dd_base)
        return
    else:
        d = doc.get_by_loc(state.db, this)
        assert d is not None

        skip = not (d.loc.endswith("index.sxml") or state.force or d.update_timestamp_ns > state.last_update_ns)
        if skip:
            return

        bcx = generate_breadcrumb(bc, this.replace("/index.sxml", ""))
        if this.endswith("/index.sxml"):
            bc.append((parent if parent else "/", d.title))

        y = sxml.parse(d.text)
        sxml.move_node_to_end(y, "/document/source")
        sxml.move_node_to_end(y, "/document/copyright")
        sxml.move_node_to(y, "/document/title", 0)

        df = f"{dd}{this}"
        df = df.replace(".sxml", ".html")
        print(f"PUBLISHING {this} => {d.title} => {df}")
        html = __to_html(state, y, this, d.title, bcx)
        fs.write_text(df, html)