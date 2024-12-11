from asgi_csrf import asgi_csrf
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.routing import Route
from mod.env import env
from mod.root.http import login, static, home, sa, logout

TRUE_ON_PRODUCTION = env.IS_PRODUCTION
FALSE_ON_PRODUCTION = not env.IS_PRODUCTION
DOMAIN = "app.adhyeta.org.in" if env.IS_PRODUCTION else None

middleware = []
if env.IS_PRODUCTION:
    # from starlette.middleware.authentication import AuthenticationMiddleware
    middleware.append(Middleware(TrustedHostMiddleware))
middleware.append(Middleware(SessionMiddleware, secret_key=env.SESSION_SECRET_KEY, https_only=TRUE_ON_PRODUCTION, max_age = None, same_site = "strict", domain = DOMAIN))

asgi_app = asgi_csrf(Starlette(
    debug=FALSE_ON_PRODUCTION,
    routes=[
        Route('/sa/k/{path:path}', sa.exec),
        Route('/a/{file}', static.exec),
        Route('/', home.exec),
        Route('/favicon.ico', static.exec_favicon),
        Route('/login', login.exec, methods=["GET", "POST"]),
        Route('/logout', logout.exec),
    ],
    middleware=middleware
), signing_secret=env.CSRF_SECRET_KEY)