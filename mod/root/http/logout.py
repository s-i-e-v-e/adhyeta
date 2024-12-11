from mod.root.http import Request, RedirectResponse

async def exec(request: Request):
    request.session.pop("user", None)
    return RedirectResponse("/", status_code = 303)