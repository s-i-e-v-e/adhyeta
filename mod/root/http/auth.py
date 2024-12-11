from mod.root.data import user, db, Any
from mod.root.http import WWW_URL, Request, redirect_to, session, get_csrf_token, as_html_response, set_renderer


def get_next(x) -> str:
    return x["next"] if "next" in x else "/"

def get_html(request: Request, error_class: str, next: str) -> str:
    return f"""
    <div id="login" loc="/" title="Log In">
        <div class="{error_class}"><h2>Log In</h2>
        <form hx-post="/login" hx-target="#login">
            <input type="hidden" name="next" value="{next}">
            <input type="hidden" name="csrftoken" value="{get_csrf_token(request)}">
            <p><input type="text" autocomplete="" name="username" placeholder="Username/Email"></p>
            <p><input type="password" name="password" placeholder="Password"></p>
            <p class="message"><span>Invalid Username/Email/Password</span></p>
            <p><button type="submit" name="login">Log In</button></p>
            <div style="text-align:center; max-width:20ch; margin: auto;">This is where you log into the app. If all you want to do is read the content without interacting with it, visit the <a href="{WWW_URL}">MAIN</a> website.</div>
        </form>
        </div>
    </div>
    """

def render_login(request: Request):
    next = get_next(request.query_params)
    if not session.is_valid(request):
        return as_html_response(request, get_html(request, "", next))
    else:
        u = session.validate(request)
        assert u is not None
        return redirect_to(request, next)

def __authenticate(xx: Any, user_k: str, pass_k: str):
    if user_k not in xx or pass_k not in xx:
        return None

    u = xx[user_k]
    p = xx[pass_k]
    return user.validate(db, u, p)

async def login(request: Request):
    if "POST" in request.method:
        f = await request.form()
        next = get_next(f)

        uid = __authenticate(f, "username", "password")
        if not uid:
            return get_html(request, "error", next)

        request.session["user"] = uid

        u = session.validate(request)
        assert u is not None
        return redirect_to(request, next)
    else:
        return render_login(request)

async def logout(request: Request):
    session.validate(request)

    request.session.pop("user", None)
    return redirect_to(request, "/login")

set_renderer("/login", render_login)