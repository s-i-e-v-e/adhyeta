from mod.lib import crypto
from mod.root.data.private import Database, Row, dataclass

@dataclass
class User:
    id: int
    user: str
    email: str
    hash: str

def __build(xs: Row):
    return User(xs[0], xs[1], xs[2], xs[3])

def load(db: Database, user_or_email: str):
    xs = db.exec("SELECT id, user, email, hash FROM users WHERE user = ? or email = ?", user_or_email, user_or_email)
    return None if len(xs) == 0 else __build(xs[0])

def load_by_id(db: Database, user_id: int):
    xs = db.exec("SELECT id, user, email, hash FROM users WHERE id = ?", user_id)
    return None if len(xs) == 0 else __build(xs[0])

def is_admin(db: Database, user_id: int):
    return user_id == 1

def validate(db: Database, user_or_email: str, password: str):
    u = load(db, user_or_email)
    if not u:
        crypto.hash_password_argon2id(password)
        return None

    success, hash = crypto.verify_password_argon2id(u.hash, password)
    if hash:
        db.exec("UPDATE users SET hash = ? WHERE user = ? or email = ?", hash, user_or_email, user_or_email)

    return u.id if success else None

def add(db: Database, user: str, email: str, password: str) -> bool:
    hash = crypto.hash_password_argon2id(password)
    u1 = load(db, user)
    u2 = load(db, email)
    if u1 or u2:
        return False

    db.exec("INSERT INTO users(user, email, hash) VALUES(?, ?, ?)", user, email, hash)
    return True