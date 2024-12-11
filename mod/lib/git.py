from mod.lib import fs

def commit_exists(repo: str, hash: str) -> bool:
    try:
        fs.exec(
            ["git", "show", hash],
            cwd=repo,
        )
        return True  # Commit exists
    except Exception:
        return False  # Commit does not exist
