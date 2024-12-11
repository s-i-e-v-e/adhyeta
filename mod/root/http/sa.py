import typing

from mod.lib import sxml, text
from mod.root.backend.importers.sxml_list import handle_list_pragma
from mod.root.backend.importers.traversal import sxml_validate_doc
from mod.root.backend.importers.traversal.sxml_recognize_words import recognize_words
from mod.root.backend.importers.traversal.sxml_vyakaranam import vyakaranam
from mod.root.backend.importers.sxml_node_as_html import generate_breadcrumb, page_has_words
from mod.root.backend.importers.traversal.sxml_render_document_as_html import sxml_to_str

from mod.root.data import doc, db, word
from mod.root.http import Request, session, as_html_response, get_csrf_token


def get_breadcrumb(d: doc.Doc):
    xs = d.loc.split("/")[:-1]
    ys = []
    p = ""
    for x in xs:
        p += x
        p += "/"
        pp = p
        pp += "/index.sxml"
        pp = pp.replace("//", "/")
        dd = doc.get_by_loc(db, pp)
        if dd:
            loc = dd.loc.replace(".sxml", ".html").replace("/index.html", "")
            loc = loc if loc else "/"
            ys.append((loc, dd.title))
    return generate_breadcrumb(ys, d.loc.replace("/index.sxml", ""))

def __process(d: doc.Doc, csrftoken: str):
    text = d.text.replace("(document ",
                          f"""(document @csrftoken "{csrftoken}" """)
    n = sxml.parse(text)
    sxml_validate_doc.validate(n)
    sxml.move_node_to_end(n, "/document/meta/source")
    sxml.move_node_to_end(n, "/document/meta/copyright")
    sxml.move_node_to(n, "/document/meta/title", 0)
    return n, doc.meta_to_metadata(d.metadata)

def get_progress_sxml(uuid: str, user_id: int):
    unique_words = word.count_by_doc(db, uuid)
    known_words = word.count_by_user_and_doc(db, uuid, user_id)
    pc = int(round(known_words * 100.0 / unique_words, 0))
    return sxml.parse(f"""(meta @id progress (p (progress @max {unique_words} @value {known_words} @title "{pc}% - {known_words}/{unique_words} words")))""")

def get_tab_sxml(uuid: str, selected: int):
    re_vals = text.to_json({'get': 're', 'doc_uuid': uuid})
    vy_vals = text.to_json({'get': 'vy', 'doc_uuid': uuid})

    re_selected = ' @selected ""' if selected == 0 else ''
    vy_selected = ' @selected ""' if selected == 1 else ''
    n = sxml.parse(f"""(div @class tabs @hx-target ".document-container" @hx-swap "outerHTML" (a @href "javascript:void(0);" @hx-post "/sa/" @hx-vals "" {re_selected} Reader)(a @href "javascript:void(0);" @hx-post "/sa/" @hx-vals "" {vy_selected} Grammar [WIP]))""")

    n.node(0).attrs["hx-vals"] = re_vals
    n.node(1).attrs["hx-vals"] = vy_vals
    return n

def render_vyakaranam_page(d: doc.Doc, csrftoken: str, user_id: int, floc: str):
    n, meta = __process(d, csrftoken)
    handle_list_pragma(db, n, "/".join(floc.split("/")[0:-1]))

    is_index = page_has_words(n, meta)
    if not is_index:
        vyakaranam(n)
        sxml.insert_node(n, "/document/matter", get_progress_sxml(n.attrs["uuid"], user_id), -1)

    sxml.insert_node(n, "/document/matter", sxml.parse("(hr)"), -1)
    if not is_index:
        sxml.insert_node(n, "/document/matter", get_tab_sxml(d.uuid, 1), -1)
    sxml.insert_node(n, "/document/matter", sxml.parse("(hr)"), 1)
    _, matter = sxml.filter_node(n, "/document/matter")
    assert matter is not None
    tc = sxml.parse("(div @class tab-container)")
    tc.xs.append(matter)
    sxml.replace_node(n, "/document/matter", tc)
    html = """<div class="document-container vyakaranam">"""
    html += get_breadcrumb(d)
    html += sxml_to_str(n)
    html += """</div>"""
    return html

def render_page(d: doc.Doc, csrftoken: str, user_id: int, floc: str):
    n, meta = __process(d, csrftoken)
    handle_list_pragma(db, n, "/".join(floc.split("/")[0:-1]))

    is_index = page_has_words(n, meta)
    if not is_index:
        recognize_words(n, user_id)
        sxml.insert_node(n, "/document/matter", get_progress_sxml(n.attrs["uuid"], user_id), -1)

    sxml.insert_node(n, "/document/matter", sxml.parse("(hr)"), -1)
    if not is_index:
        sxml.insert_node(n, "/document/matter", get_tab_sxml(d.uuid, 0), -1)
    sxml.insert_node(n, "/document/matter", sxml.parse("(hr)"), 1)
    _, matter = sxml.filter_node(n, "/document/matter")
    assert matter is not None
    tc = sxml.parse("(div @class tab-container)")
    tc.xs.append(matter)
    sxml.replace_node(n, "/document/matter", tc)
    html = """<div class="document-container">"""
    html += get_breadcrumb(d)
    html += sxml_to_str(n)
    html += """</div>"""
    return html

def get_note_form(user_id: int, w: str, xid: str):
    ww = word.get(db, w)
    assert ww is not None
    note = word.get_note(db, user_id, ww.hash)
    html = f"""<div hx-swap-oob="true" hash={ww.hash.hex()} id="id_{xid}" class="tag-container">
        <form>
        <p><textarea placeholder="note" cols="25" rows="6" name="note">{note[0] if note else ""}</textarea></p>
        <p><button hx-post="/sa/" hx-target="#ephemeral + div" type="submit">Submit</button><a class="cancel" href="javascript:void(null);">Cancel</a></p>
        </form>
    </div>"""
    return html

def translate_path(p: str):
    if not p.endswith('.html'):
        p = p + '/index.html'
    p = p.replace(".html", ".sxml")
    p = p.replace("//", "/")
    return p

async def exec(request: Request):
    u = session.validate(request)
    assert u is not None

    p = translate_path(request.url.path)
    if request.method == 'GET':
        csrftoken = get_csrf_token(request)
        d = doc.get_by_loc(db, p)
        assert d is not None
        html = render_page(d, csrftoken, u.id, p)
        return as_html_response(request, html)
    elif request.method == 'POST':
        f = await request.form()
        f = typing.cast(typing.Dict[str, str], f)

        html = ''
        doc_uuid = f["doc_uuid"]
        if "action" in f:
            w = f["word"]
            action = f["action"]
            if action == "mark":
                word.known(db, u.id, w)
            elif action == "flag":
                word.flag(db, w)
            elif action == "tag":
                html += get_note_form(u.id, w, f["xid"])
            else:
                raise Exception("Unknown action")
            html += sxml_to_str(get_progress_sxml(doc_uuid, u.id))
        elif "note" in f:
            word.note(db, u.id, bytes.fromhex(f["hash"]), f["note"])
            d = doc.get_by_uuid(db, doc_uuid)
            assert d is not None
            csrftoken = get_csrf_token(request)
            html += render_page(d, csrftoken, u.id, d.loc)
        elif "get" in f:
            d = doc.get_by_uuid(db, doc_uuid)
            assert d is not None
            csrftoken = get_csrf_token(request)
            if f["get"] == "re":
                html = render_page(d, csrftoken, u.id, d.loc)
            elif f["get"] == "vy":
                html = render_vyakaranam_page(d, csrftoken, u.id, d.loc)
            else:
                raise Exception("Unknown action")
        else:
            raise Exception("Unknown action")

        return as_html_response(request, html)
