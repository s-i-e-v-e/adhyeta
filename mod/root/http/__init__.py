from typing import Callable

from starlette.requests import Request
from starlette.responses import Response, FileResponse, HTMLResponse, RedirectResponse

from mod.config import env
from mod.lib import fs, sxml
from mod.root.backend.importers.traversal.sxml_render_document_as_html import sxml_to_html, sxml_to_str

TEMPLATE_HTML = sxml_to_html(sxml_to_str(sxml.parse(fs.read_text("./static/app.template.sxml"))), "", "", "")
SESSION_MARKER_HTML = """<span id="session" is-session="0"></span>"""
GET_RENDERERS = {}
GetHandler = Callable[[Request], RedirectResponse|HTMLResponse]

WWW_URL = "https://www.adhyeta.org.in" if env.IS_PRODUCTION else "http://127.0.0.1:8088"
APP_URL = "https://app.adhyeta.org.in" if env.IS_PRODUCTION else "http://127.0.0.1:8000"

def set_renderer(url: str, handler: GetHandler):
    GET_RENDERERS[url] = handler

def __session_marker(request: Request):
    from mod.root.http import session
    return f"""<span hx-swap-oob="true" id="session" is-session="{1 if session.is_valid(request) else 0}"></span>"""

def as_html_response(request: Request, x: str):
    hx = "HX-Request" in request.headers
    if not hx:
        x = TEMPLATE_HTML.replace("{{main}}", x).replace(SESSION_MARKER_HTML, __session_marker(request))
    else:
        x += __session_marker(request)
    return HTMLResponse(x)

def redirect_to(request: Request, next: str) -> RedirectResponse|HTMLResponse:
    hx = "HX-Request" in request.headers
    if hx and next in GET_RENDERERS:
        x = GET_RENDERERS[next](request)
        x.headers["Hx-Replace-Url"] = next
        return x
    else:
        return RedirectResponse(next, status_code=303)


def get_csrf_token(request: Request):
    return request.scope["csrftoken"]()