from mod.config import env
from mod.lib import crypto, fs
from mod.root.data import db
from mod.root.action.pub import State
from mod.root.action.pub.import_work import import_files_into_db
from mod.root.action.pub.publish_www import publish_files
from mod.root.action.pub.vfs import build_vfs


def generate_caddy_hash(d: str):
    EXT = ".b3"
    for f in fs.list_dirs(d):
        generate_caddy_hash(f.full_path)

    for f in fs.list_files(d):
        if f.name.endswith(EXT):
            continue
        digest = crypto.blake3(f.full_path).hex()

        hash_file = f"{f.full_path}{EXT}"
        with open(hash_file, "w") as fp:
                fp.write(digest)

def do_import(force: bool):
    # get last time sxml files were published to www
    sync_file = f"{env.DATA_ROOT}/sync.last"
    last_update_time_ns = fs.stat(sync_file).st_mtime_ns if fs.exists(sync_file) else 0
    # last_update_time_ns = 0

    state = State(db, force, last_update_time_ns)
    # get files updated after this time
    try:
        db.begin()
        for f in [env.SXML_TEXTS_ROOT, env.SXML_WWW_ROOT]:
            import_files_into_db(state, fs.to_file(f))
        db.commit()
    except Exception as ex:
        db.rollback()
        raise ex
    fs.write_text(sync_file, "")

    do_publish(state)

def do_publish(state: State):
    vfs = build_vfs(db)
    publish_files(state, vfs, "", "", [], env.WWW_ROOT, env.WWW_ROOT)
    generate_caddy_hash(env.WWW_ROOT)