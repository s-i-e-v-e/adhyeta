from starlette.exceptions import HTTPException

from mod.root.data import user, db
from mod.root.http import Request, RedirectResponse, Response, as_html_response

def is_valid(request: Request):
    return "user" in request.session

def validate(request: Request, as_admin=False):
    if not is_valid(request):
        raise HTTPException(status_code=404, detail=request.url.path)
    u = user.load_by_id(db, request.session["user"])
    assert u is not None
    if as_admin and not user.is_admin(db, u.id):
        raise HTTPException(status_code=403, detail=request.url.path)
    return u

def handle_403(request: Request, e: HTTPException) -> Response:
    return as_html_response(request, "<h1>403 Forbidden</h1>")

def handle_404(request: Request, e: HTTPException) -> Response:
    return RedirectResponse(f"/login?next={e.detail}")