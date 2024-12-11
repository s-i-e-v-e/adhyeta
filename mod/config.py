from dataclasses import dataclass
from mod.lib import fs

@dataclass
class Env:
    RAW_ROOT: str # raw GRETIL/DCS/ETC texts
    SXML_ROOT: str  # sxml www

    CACHE_ROOT: str  # cache
    DATA_ROOT: str  # database
    WWW_ROOT: str # root: www.adhyeta.org.in

    IS_PRODUCTION: bool

    SESSION_SECRET_KEY: str
    CSRF_SECRET_KEY: str
    ROOT_USER: str
    DEEPSEEK_API_KEY: str

env = Env("/tmp/.abc", "/tmp/.abc", "/tmp/.abc", "/tmp/.abc", "/tmp/.abc", False, "", "", "", "")

import pathlib
env_file = (pathlib.Path(__file__).parent.parent / ".env").__str__()
for x in fs.read_text(env_file).split("\n"):
    if not x.strip():
        continue
    y = x.split("=")

    a = y[0]
    b = (True if y[1] == "True" else False) if y[0].startswith("IS_") else y[1]
    env.__setattr__(a, b)

if not env.SESSION_SECRET_KEY or not env.CSRF_SECRET_KEY:
    raise ValueError("No SECRET_KEY set")