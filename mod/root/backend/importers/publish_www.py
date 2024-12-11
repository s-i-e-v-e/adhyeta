from dataclasses import dataclass

from mod.lib import sxml
from mod.lib import fs
from mod.lib.sqlite_db import Database
from mod.root.backend.importers.sxml_list import handle_list_pragma, handle_table_pragma
from mod.root.backend.importers.traversal.sxml_recognize_words import recognize_words
from mod.root.backend.importers.traversal.sxml_render_document_as_html import sxml_to_html, sxml_to_str
from mod.root.backend.importers.sxml_node_as_html import generate_breadcrumb, BreadCrumbs, page_has_words
from mod.root.data import doc, word

TEMPLATE_HTML = sxml_to_str(sxml.parse(fs.read_text("./static/www.template.sxml")))

@dataclass
class State:
    db: Database
    force: bool
    last_update_ns: int

def build_state(db: Database, force: bool, last_update_ns: int) -> State:
    return State(db, force, last_update_ns)

def __handle_word_count(state: State, meta: doc.DocMetadata, n: sxml.SxmlNode):
    unique_words = word.count_by_doc(state.db, n.attrs["uuid"])
    if page_has_words(n, meta):
        sxml.insert_node(n, "/document/matter", sxml.parse(f"(meta (p Unique Words: {unique_words}))"), -1)

def __to_html(state: State, meta: doc.DocMetadata, y: sxml.SxmlNode, title: str, bcx: str):
    parent = "/".join(meta.original_loc.split("/")[0:-1])
    handle_list_pragma(state.db, y, parent)
    handle_table_pragma(state.db, y, parent)
    if not meta.original_loc.endswith("/index.sxml"):
        __handle_word_count(state, meta, y)
    if sxml.sxml_index_of(y, "/document/matter") > 0:
        sxml.insert_node(y, "/document/matter", sxml.parse("(hr)"), 0)
    sxml.insert_node(y, "/document/matter", sxml.parse("(hr)"), 1)
    recognize_words(y, 0)
    html = sxml_to_str(y)
    return sxml_to_html(TEMPLATE_HTML, html, title, bcx)

def publish_files(state: State, vfs: doc.VirtualFS, parent: str, this: str, bc: BreadCrumbs, dd: str, dd_base: str):
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
        sxml.move_node_to_end(y, "/document/meta/source")
        sxml.move_node_to_end(y, "/document/meta/copyright")
        sxml.move_node_to(y, "/document/meta/title", 0)

        df = f"{dd}{this}"
        df = df.replace(".sxml", ".html")
        print(f"PUBLISHING {this} => {d.title} => {df}")
        html = __to_html(state, doc.meta_to_metadata(d.metadata), y, d.title, bcx)
        fs.write_text(df, html)