from mod.root.http import Request, RedirectResponse

def is_valid(request: Request):
    return "user" in request.session

def validate(request: Request):
    if not is_valid(request):
        return RedirectResponse(f"/login?next={request.url.path}")
