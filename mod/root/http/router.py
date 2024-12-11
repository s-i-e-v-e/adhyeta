from asgi_csrf import asgi_csrf
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.routing import Route
from mod.config import env
from mod.lib import fs
from mod.root.http import auth, static, home, sa, admin, session

def init_repo():
    from mod.root.data import repo
    repo.init()

def install_assets():
    fs.copy_tree("./www", env.WWW_ROOT)
    fs.copy_tree(f"{env.SXML_ROOT}/a", f"{env.WWW_ROOT}/a")
    import subprocess
    subprocess.run(["rollup", "main.js", "--file", f"{env.WWW_ROOT}/a/app.js", "--format", "iife"], cwd=f"{env.WWW_ROOT}/a/js")

TRUE_ON_PRODUCTION = env.IS_PRODUCTION
FALSE_ON_PRODUCTION = not env.IS_PRODUCTION
DOMAIN = "app.adhyeta.org.in" if env.IS_PRODUCTION else None

middleware = []
if env.IS_PRODUCTION:
    # from starlette.middleware.authentication import AuthenticationMiddleware
    middleware.append(Middleware(TrustedHostMiddleware))
middleware.append(Middleware(SessionMiddleware, secret_key=env.SESSION_SECRET_KEY, https_only=TRUE_ON_PRODUCTION, max_age = None, same_site = "strict", domain = DOMAIN))

init_repo()
install_assets()

asgi_app = asgi_csrf(Starlette(
    debug=FALSE_ON_PRODUCTION,
    routes=[
        Route('/a/{path:path}', static.handle),
        # Route('/favicon.ico', static.handle_favicon),
        # Route('/robots.txt', static.handle_robots),
        Route('/login', auth.login, methods=["GET", "POST"]),

        Route('/', home.handle),
        Route('/logout', auth.logout),
        Route('/admin', admin.handle),
        Route('/admin/import', admin.handle_import),
        Route('/sa/{path:path}', sa.exec, methods=["GET", "POST"]),
    ],
    exception_handlers={403: session.handle_403, 404: session.handle_404},
    middleware=middleware
), signing_secret=env.CSRF_SECRET_KEY)