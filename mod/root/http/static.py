from mod.root.http import Request, FileResponse
from mod.config import env

async def exec(request: Request):
    fn = f"{env.WWW_ROOT}/a/{request.path_params.get('file')}"
    return FileResponse(fn)

async def exec_favicon(request: Request):
    fn = f"{env.WWW_ROOT}/favicon.ico"
    return FileResponse(fn)