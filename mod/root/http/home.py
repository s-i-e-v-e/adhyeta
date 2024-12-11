from mod.root.data import user
from mod.root.http import Request, HTMLResponse, to_html, session, db

async def exec(request: Request):
    invalid = session.validate(request)
    if invalid:
        return invalid

    u = user.load_by_id(db, request.session["user"])
    assert u is not None
    return to_html(request, "index.html", {"USER": u.user})
