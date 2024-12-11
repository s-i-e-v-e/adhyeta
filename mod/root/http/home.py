from mod.root.http import set_renderer, Request, session, as_html_response
from mod.root.data import user, db


def render_page(request: Request):
    u = session.validate(request)
    assert u is not None

    html = """
    <h1>Read</h1>
    <ul>"""
    if user.is_admin(db, u.id):
        html += """<li><a href="/admin">Admin</a></li>"""

    html += """<li><a href="/sa/k/">कथाः</a></li>
        <li><a href="/sa/itihasa/valmikiramayanam-bce/">वाल्मीकिरामायणम् BCE</a></li>
    </ul>
    """
    return as_html_response(request, html)

async def handle(request: Request):
    u = session.validate(request)
    assert u is not None

    return render_page(request)

set_renderer("/", render_page)