from mod.env import env
from mod.lib.fs import read_text
from mod.root.http import Request, HTMLResponse, session


async def exec(request: Request):
    invalid = session.validate(request)
    if invalid:
        return invalid

    p = request.url.path
    if not p.endswith('.html'):
        p = p + '/index.html'
    x = read_text(f"{env.WWW_ROOT}/{p}")
    return HTMLResponse(x)