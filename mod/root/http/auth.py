import typing
from mod.root.http import Request, RedirectResponse, to_html, db
from mod.root.http import session
from mod.root.data import user

def __authenticate(xx: typing.Any, user_k: str, pass_k: str):
    if user_k not in xx or pass_k not in xx:
        return None

    u = xx[user_k]
    p = xx[pass_k]
    return user.validate(db, u, p)

async def login(request: Request):
    def get_next(x) -> str:
        return x["next"] if "next" in x else "/"

    def get_html(next: str, show_error = False):
        return to_html(request, "login.html", {
            "USER": "",
            "NEXT": next,
            "CSRF_TOKEN": request.scope["csrftoken"](),
            "ERROR_MESSAGE_CLASS": "error" if show_error else ""
        })

    if "POST" in request.method:
        f = await request.form()
        next = get_next(f)

        uid = __authenticate(f, "username", "password")
        if not uid:
            return get_html(next, show_error = True)

        request.session["user"] = uid
        return RedirectResponse(next, status_code=303)
    else:
        next = get_next(request.query_params)
        if not session.is_valid(request):
            return get_html(next, show_error=False)

        return RedirectResponse(next)

async def logout(request: Request):
    session.validate(request)

    request.session.pop("user", None)
    return RedirectResponse("/", status_code = 303)