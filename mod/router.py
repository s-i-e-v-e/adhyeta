from starlette.applications import Starlette
from starlette.responses import FileResponse
from starlette.routing import Route, Mount
from starlette.requests import Request

from mod.word import word_list_page_render


async def assets(request: Request):
    file = '/a/' + request.path_params['file']
    return FileResponse('./www'+file)


async def home(request: Request):
    return await work_list(request)

from starlette.requests import Request
from starlette.responses import HTMLResponse

from mod.work import work_list_page_render, work_parts_list_page_render, part_page_render
from mod.repo.db import Database
from mod.repo.works import works_import_all
from mod.util.fs import read_text


def __to_html(request: Request, html: str):
    hx = "HX-Request" in request.headers
    if hx:
        return HTMLResponse(html)
    else:
        return HTMLResponse(read_text('./www/index.html').replace("{{content}}", html))


async def work_list(request: Request):
    html = work_list_page_render()
    return __to_html(request, html)


async def work_render(request: Request):
    work_id = request.path_params['work_id']
    html = work_parts_list_page_render(work_id)
    return __to_html(request, html)


async def part_render(request: Request):
    work_id = request.path_params['work_id']
    part_id = request.path_params['part_id']
    fd = await request.form()

    w = int(fd["w"]) if "w" in fd else 0
    trigger = fd["xt"] if "xt" in fd else ""
    note = fd["note"] if "note" in fd else ""
    html = part_page_render(work_id, part_id, w, trigger, note)
    return __to_html(request, html)

async def word_list(request: Request):
    word_id = int(request.path_params['word_id'])
    html = word_list_page_render(word_id)
    return __to_html(request, html)

def init():
        db = Database()
        db.init()
        works_import_all()

router = Starlette(debug=True, routes=[
    Route('/a/{file}', assets),
    Route('/', home),
    Route('/e/word/{word_id}', word_list),
    Mount('/e/work', routes=[
        Route('/', work_list, methods=['GET']),
        Route('/{work_id}', work_render, methods=['GET']),
        Route('/{work_id}/part/{part_id}', part_render, methods=['GET', 'PUT']),
    ])
])

init()
