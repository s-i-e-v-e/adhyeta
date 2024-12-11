from mod.root.data import user, db, Any
from mod.root.http import Request, redirect_to, to_html_from_file, session


def __authenticate(xx: Any, user_k: str, pass_k: str):
    if user_k not in xx or pass_k not in xx:
        return None

    u = xx[user_k]
    p = xx[pass_k]
    return user.validate(db, u, p)

def get_csrf_token(request: Request):
    return request.scope["csrftoken"]()

async def login(request: Request):
    def get_next(x) -> str:
        return x["next"] if "next" in x else "/"

    def get_html(next: str, show_error = False):
        return to_html_from_file(request, "/login", {
            "USER": "",
            "NEXT": next,
            "CSRF_TOKEN": get_csrf_token(request),
            "ERROR_MESSAGE_CLASS": "error" if show_error else ""
        })

    if "POST" in request.method:
        f = await request.form()
        next = get_next(f)

        uid = __authenticate(f, "username", "password")
        if not uid:
            return get_html(next, show_error = True)

        request.session["user"] = uid
    else:
        next = get_next(request.query_params)
        if not session.is_valid(request):
            return get_html(next, show_error=False)
    u = session.validate(request)
    assert u is not None
    return redirect_to(request, next, {"USER": u.user})

async def logout(request: Request):
    session.validate(request)

    request.session.pop("user", None)
    return redirect_to(request, "/login", {})