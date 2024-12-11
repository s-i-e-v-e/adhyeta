from mod.lib import sxml
from mod.lib import fs
from mod.root.action.sxml_html import generate_breadcrumb, BreadCrumbs
from mod.root.action import sxml_validate_doc
from mod.root.action.sxml_list import handle_list_pragma
from mod.root.action.sxml_publish_html import sxml_to_html, sxml_to_str
from mod.root.action.sxml_recognize_words import recognize_words
from mod.root.data import doc, word
from mod.root.action.pub import VirtualFS, State

TEMPLATE_HTML = sxml_to_str(sxml.parse(fs.read_text("./static/www.template.sxml")))

def handle_word_count(state: State, n: sxml.SxmlNode, floc: str):
    unique_words = word.count_by_doc(state.db, n.attrs["uuid"])
    if sxml.node_exists(n, "/document/sec") and not [x for x in ["index.sxml", "copyright.sxml"] if floc.endswith(x)]:
        sxml.insert_node(n, "/document/sec", sxml.parse(f"(meta (p Unique Words: {unique_words}))"), -1)

def __to_html(state: State, y: sxml.SxmlNode, floc: str, title: str, bcx: str):
    sxml_validate_doc.validate(y)
    handle_list_pragma(state.db, y, floc)
    if not floc.endswith("/index.html"):
        handle_word_count(state, y, floc)
    if sxml.sxml_index_of(y, "/document/sec") > 0:
        sxml.insert_node(y, "/document/sec", sxml.parse("(hr)"), -1)
    sxml.insert_node(y, "/document/sec", sxml.parse("(hr)"), 1)
    recognize_words(y, 0)
    html = sxml_to_str(y)
    return sxml_to_html(TEMPLATE_HTML, html, title, bcx)

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