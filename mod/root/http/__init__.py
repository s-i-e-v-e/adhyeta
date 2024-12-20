from starlette.requests import Request
from starlette.responses import FileResponse, HTMLResponse, RedirectResponse

from mod.env import env
from mod.lib.fs import read_text
from mod.root.data.repo import repo as db
from html import escape
def to_html(request: Request, p: str, replacers: dict[str, str]):
    x = read_text(f"{env.APP_ROOT}/{p}")
    for k in replacers:
        a = "{{"
        a += k
        a += "}}"
        x = x.replace(a, escape(replacers[k]))

    hx = "HX-Request" in request.headers
    if hx:
        return HTMLResponse(x)
    else:
        template_html = read_text(f"{env.APP_ROOT}/app.template.html")
        return HTMLResponse(template_html.replace("{{main}}", x))