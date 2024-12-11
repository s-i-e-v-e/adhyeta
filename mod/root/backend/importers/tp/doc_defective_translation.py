# detect translation failures
from mod.lib import fs
import re

def __has_en_text(fp: str) -> bool:
    paras = fs.read_text(fp).split('\n')
    for p in paras:
        m = re.match(r'(<p>"?[a-zA-Z \-,:;.?!<>/]+)', p)
        if m:
            for x in m.groups():
                print(x)
    return False

def __find(fp: str):
    for f in fs.list_dirs(fp):
        __find(f.full_path)

    for f in fs.list_files(fp):
        if not f.name.endswith(".sa.xml"):
            continue
        print(f.full_path)
        __has_en_text(f.full_path)

def find(path: str):
    __find(path)
