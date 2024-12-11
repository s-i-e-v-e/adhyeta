from mod.config import env
from mod.lib import fs
from mod.root.http import Request, HTMLResponse, session


async def exec(request: Request):
    invalid = session.validate(request)
    if invalid:
        return invalid

    p = request.url.path
    if not p.endswith('.html'):
        p = p + '/index.html'
    x = fs.read_text(f"{env.WWW_ROOT}/{p}")
    return HTMLResponse(x)