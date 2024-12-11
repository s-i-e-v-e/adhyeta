from starlette.exceptions import HTTPException
from mod.root.http import Request, RedirectResponse

def is_valid(request: Request):
    return "user" in request.session

def validate(request: Request):
    if not is_valid(request):
        raise HTTPException(status_code=403, detail=request.url.path)

def handle_404(request: Request, e: HTTPException) -> RedirectResponse:
    return RedirectResponse(f"/login?next={e.detail}")