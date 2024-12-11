from mod.root.http import Request, FileResponse
from mod.config import env

async def handle(request: Request):
    fn = f"{env.WWW_ROOT}{request.url.path}"
    return FileResponse(fn)

# async def handle_favicon(request: Request):
#     fn = f"{env.WWW_ROOT}/favicon.ico"
#     return FileResponse(fn)
#
# async def handle_robots(request: Request):
#     fn = f"{env.WWW_ROOT}/robots.txt"
#     return FileResponse(fn)