import html
from starlette.requests import Request
from starlette.responses import FileResponse, HTMLResponse, RedirectResponse

from mod.config import env
from mod.lib import fs
from mod.root.data import db

template_html = fs.read_text(f"{env.APP_ROOT}/app.template.html")

page_map = {
    "/": "index.html",
    "/login": "login.html",
}

def to_html(request: Request, x: str, replacers: dict[str, str]):
    hx = "HX-Request" in request.headers
    if not hx:
        x = template_html.replace("{{main}}", x)

    for k in replacers:
        a = "{{"
        a += k
        a += "}}"
        x = x.replace(a, html.escape(replacers[k]))

    return HTMLResponse(x)

def to_html_from_file(request: Request, p: str, replacers: dict[str, str]):
    x = fs.read_text(f"{env.APP_ROOT}/{page_map[p]}")
    return to_html(request, x, replacers)

def redirect_to(request: Request, next: str, replacers: dict[str, str]):
    hx = "HX-Request" in request.headers
    if hx:
        x = to_html_from_file(request, next, replacers)
        x.headers["Hx-Replace-Url"] = next
        return x
    else:
        return RedirectResponse(next, status_code=303)