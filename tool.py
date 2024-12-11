import sys

import blake3
import mod.tool.ocr as ocr
import mod.tool.uuid as uuid

if __name__ == '__main__':
    if sys.argv[1] == "ocr":
        dir_in = sys.argv[2]
        base = sys.argv[3]
        ocr.run(dir_in, base)
    elif sys.argv[1] == "uuid":
        uuid.run()
    elif sys.argv[1] == "user":
        from mod.lib.crypto import random_str
        from mod.root.data import repo, user
        un = sys.argv[2]
        pw = random_str(16)
        user.add(repo.repo, un, f"{un}@localhost", pw)
        print(f"{un}-{pw}")
        print(repo.repo.head("SELECT * FROM users WHERE user = ?", un))
    elif sys.argv[1] == "ext":
        from mod.config import env
        from mod.raw import ramayana
        ramayana.generate(env.RAW_ROOT, env.SXML_TEXTS_ROOT)
    elif sys.argv[1] == "vy":
        from mod.root.data.y_classify import classify
        classify()
    elif sys.argv[1] == "hash":
        from mod.lib.crypto import blake3_128
        print(blake3_128(sys.argv[2]).hex())
    else:
        pass
