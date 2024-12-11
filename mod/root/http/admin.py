from mod.env import env
from mod.lib.fs import stat, exists, to_file, copy_tree, write_text
from mod.root.action.pub.ramayana import do_import_ramayana
from mod.root.action.pub.import_work import State, import_files_into_db
from mod.root.action.pub.publish_static import publish_files
from mod.root.action.pub.vfs import build_vfs
from mod.root.http import Request, db, to_html, session


async def import_(request: Request):
    session.validate(request)

    force = 'force' in request.query_params
    if force:
        do_import_ramayana(env.RAW_ROOT, env.SXML_TEXTS_ROOT)

    # get last time sxml files were published to www
    sync_file = f"{env.DATA_ROOT}/sync.last"
    last_update_time_ns = stat(sync_file).st_mtime_ns if exists(sync_file) else 0
    last_update_time_ns = 0

    state = State(db, force, last_update_time_ns)
    # get files updated after this time
    db.begin()
    for f in [env.SXML_TEXTS_ROOT, env.SXML_WWW_ROOT]:
        import_files_into_db(state, to_file(f))
    db.commit()

    fs = build_vfs(db)

    words = set()
    publish_files(state, fs, "", "", [], env.WWW_ROOT, env.WWW_ROOT, words)
    copy_tree("./www", env.WWW_ROOT)
    write_text(sync_file, "")

    # xs = list(sorted(words))
    # xs.sort()
    # write_text(f"{dd}/word.list", "\n".join(xs))

    return to_html(request, "index.html", {})