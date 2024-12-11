from mod.config import env
from mod.lib import fs

def __get_uuids_for_work(fn: str) -> list:
    if not fs.exists(fn):
        return []
    uuids = [x for x in fs.read_text(fn).split('\n') if x.strip()]
    uuids.reverse()
    return uuids

def get_uuids_for_work(name: str):
    fn = f"{env.RAW_ROOT}/uuids/{name}.ids"
    return __get_uuids_for_work(fn)
