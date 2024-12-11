import typing
from mod.root.http import Request, RedirectResponse, HTMLResponse, to_html, db
from mod.root.http import session
from mod.root.data import user

def __authenticate(xx: typing.Any, user_k: str, pass_k: str):
    if user_k not in xx or pass_k not in xx:
        return None

    u = xx[user_k]
    p = xx[pass_k]
    return user.validate(db, u, p)

async def exec(request: Request):
    def get_next(x) -> str:
        return x["next"] if "next" in x else "/"

    def get_html(show_error = False) -> str:
        return to_html(request, "login.html", {
            "USER": "",
            "NEXT": "/",
            "CSRF_TOKEN": request.scope["csrftoken"](),
            "ERROR_MESSAGE_CLASS": "error" if show_error else ""
        })

    if "POST" in request.method:
        f = await request.form()

        uid = __authenticate(f, "username", "password")
        if not uid:
            return get_html(show_error = True)

        request.session["user"] = uid
        return RedirectResponse(get_next(f), status_code=303)
    else:
        if session.is_valid(request):
            return RedirectResponse(get_next(request.query_params))

        return get_html(show_error = False)