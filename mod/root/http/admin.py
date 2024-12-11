from mod.root.backend.importers import do_import
from mod.root.http import Request, redirect_to, as_html_response, session, set_renderer


def render_page(request: Request):
    session.validate(request, as_admin=True)
    html = """
    <div @hx-trigger "click target:a">
    <h1>Actions</h1>
    <p><a href="/admin/import">Import</a></p>
    <p><a href="/admin/import?force">Force Import</a></p>
    </div>
    """
    return as_html_response(request, html)

async def handle(request: Request):
    return render_page(request)

async def handle_import(request: Request):
    session.validate(request, as_admin=True)

    force = 'force' in request.query_params
    do_import(force)

    return redirect_to(request, "/admin")

set_renderer("/admin", render_page)