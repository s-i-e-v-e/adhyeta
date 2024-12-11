from mod.config import env
from mod.lib.fs import list_dirs, list_files, stat, exists, to_file, copy_tree, write_text
from mod.root.action.pub import ramayana
from mod.root.action.pub.import_work import State, import_files_into_db
from mod.root.action.pub.publish_static import publish_files
from mod.root.action.pub.vfs import build_vfs
from mod.root.http import Request, db, to_html_from_file, session

def generate_caddy_hash(d: str):
    import hashlib
    for f in list_dirs(d):
        generate_caddy_hash(f.full_path)

    for f in list_files(d):
        if f.name.endswith(".sha256"):
            continue
        with open(f.full_path, "rb") as fp:
            digest = hashlib.file_digest(fp, "sha256").hexdigest()

        hash_file = f"{f.full_path}.sha256"
        with open(hash_file, "w") as fp:
                fp.write(digest)

async def import_(request: Request):
    session.validate(request)

    force = 'force' in request.query_params
    if force:
        ramayana.generate(env.RAW_ROOT, env.SXML_TEXTS_ROOT)

    # get last time sxml files were published to www
    sync_file = f"{env.DATA_ROOT}/sync.last"
    last_update_time_ns = stat(sync_file).st_mtime_ns if exists(sync_file) else 0
    #last_update_time_ns = 0

    state = State(db, force, last_update_time_ns)
    # get files updated after this time
    try:
        db.begin()
        for f in [env.SXML_TEXTS_ROOT, env.SXML_WWW_ROOT]:
            import_files_into_db(state, to_file(f))
        db.commit()
    except Exception as ex:
        db.rollback()
        raise ex

    fs = build_vfs(db)

    publish_files(state, fs, "", "", [], env.WWW_ROOT, env.WWW_ROOT)
    copy_tree("./www", env.WWW_ROOT)
    write_text(sync_file, "")

    generate_caddy_hash(env.WWW_ROOT)

    return to_html_from_file(request, "/", {})