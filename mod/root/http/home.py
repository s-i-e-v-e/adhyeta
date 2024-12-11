from mod.root.action.sxml_list import doc_to_html
from mod.root.http import Request, session, to_html
from mod.root.http.auth import get_csrf_token
from mod.root.data import word, db

async def exec(request: Request):
    u = session.validate(request)
    assert u is not None

    if request.method == 'GET':
        html = doc_to_html("/sa/k/l/danarahasyam.sxml", u.id, get_csrf_token(request))
        return to_html(request, html, {"USER": u.user})
    elif request.method == 'POST':
        f = await request.form()

        word_id = int(f["word_id"][1:])
        xt = f["xt"]
        w = word.get(db, word_id)
        html = f"""<a-w hx-swap-oob="true" id="w{w.id}">{w.word}</a-w>"""
        if xt == "c":
            is_known = word.word_status_toggle(db, u.id, word_id)
            if is_known:
                html = f"""<a-w hx-swap-oob="true" id="w{w.id}" is-k>{w.word}</a-w>"""

        return to_html(request, html, {})
    else:
        raise Exception(f"Unsupported HTTP method: {request.method}")
