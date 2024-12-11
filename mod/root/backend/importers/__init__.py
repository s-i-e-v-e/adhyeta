from mod.config import env
from mod.root.data import doc, db
from mod.lib import fs, crypto

def __generate_caddy_hash(d: str):
    EXT = ".b3"
    for f in fs.list_dirs(d):
        __generate_caddy_hash(f.full_path)

    for f in fs.list_files(d):
        if f.name.endswith(EXT):
            continue
        digest = crypto.blake3(f.full_path).hex()

        hash_file = f"{f.full_path}{EXT}"
        with open(hash_file, "w") as fp:
            fp.write(digest)

def __get_changed_files(hashes: list[str], ghh: str):
    hashes.reverse()
    xs = []
    for gh in hashes:
        from mod.lib import git
        if git.commit_exists(env.SXML_ROOT, gh):
            xs = fs.exec(['git', '--no-pager', 'diff', '--name-only', gh, ghh], cwd=env.SXML_ROOT)
            xs = [x.replace('www/sa/', '/sa/') for x in xs]
            xs = [fs.to_file(x) for x in xs if x.startswith('/sa/')]
            break
        else:
            hashes.remove(gh)
    hashes.reverse()
    return xs

def do_import(force: bool):
    from mod.root.backend.importers.work import import_dir_into_db, import_files_into_db
    from mod.root.backend.importers.publish_www import publish_files, build_state
    sync_file = f"{env.DATA_ROOT}/sync.last"
    last_update_time_ns = fs.stat(sync_file).st_mtime_ns if fs.exists(sync_file) else 0

    git_head_hash = fs.exec(['git', 'rev-parse', '--verify', 'HEAD'], cwd=env.SXML_ROOT)[0]
    # git hash of last commit that was imported
    git_hash = fs.read_text(sync_file).strip().split('\n')

    # get files updated after this time
    force = force or not git_hash
    if force:
        db.exec("DELETE FROM doc_words")
        db.exec("PRAGMA foreign_keys=off; DELETE FROM words")
        db.exec("DELETE FROM docs")
    try:
        db.begin()
        if force:
            base = fs.to_file(env.SXML_ROOT)
            import_dir_into_db(db, base, "")
        else:
            # import only files that have changed + files that must always be updated
            changed_files = __get_changed_files(git_hash, git_head_hash)
            import_files_into_db(db, changed_files, env.SXML_ROOT)
        db.commit()
    except Exception as ex:
        db.rollback()
        raise ex
    if not git_hash or git_hash[-1] != git_head_hash:
        git_hash.append(git_head_hash)
        fs.write_text(sync_file, '\n'.join(git_hash))

    state = build_state(db, force, last_update_time_ns)
    vfs = doc.vfs(state.db)
    publish_files(state, vfs, "", "", [], env.WWW_ROOT, env.WWW_ROOT)
    __generate_caddy_hash(env.WWW_ROOT)