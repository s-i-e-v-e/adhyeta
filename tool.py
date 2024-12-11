import sys

import mod.tool.ocr as ocr
import mod.tool.uuid as uuid

if __name__ == '__main__':
    if sys.argv[1] == "ocr":
        dir_in = sys.argv[2]
        base = sys.argv[3]
        ocr.run(dir_in, base)
    elif sys.argv[1] == "uuid":
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        uuid.run(count)
    elif sys.argv[1] == "user":
        from mod.lib.crypto import random_str
        from mod.root.data import repo, user
        un = sys.argv[2]
        pw = random_str(16)
        user.add(repo.repo, un, f"{un}@localhost", pw)
        print(f"{un}-{pw}")
        print(repo.repo.head("SELECT * FROM users WHERE user = ?", un))
    elif sys.argv[1] == "import":
        from mod.config import env
        from mod.root.backend.importers.tp import ramayana
        ramayana.generate(env.RAW_ROOT, env.SXML_ROOT)
        #se_import.process()
        #from mod.root.backend.importers.tp import gutenberg
        #gutenberg.process()
    elif sys.argv[1] == "tokens":
        from mod.raw.deepseek import get_token_count
        from mod.lib import fs
        print(get_token_count(fs.read_text(sys.argv[2])))
    elif sys.argv[1] == "translate-se":
        from mod.raw import se_translate
        se_translate.translate_work(sys.argv[2])
        # se_translate.dump_work(sys.argv[2])
    elif sys.argv[1] == "vy":
        from mod.root.action.vyakaranam import y_classify
        y_classify.classify()
    elif sys.argv[1] == "to-xml":
        from mod.lib import fs, sxml
        print(sys.argv[2])
        for f in fs.list_files(sys.argv[2]):
             fs.write_text(f.full_path.replace('.sxml', '.xml'),sxml.to_xml(sxml.parse(fs.read_text(f.full_path))))
    elif sys.argv[1] == "hash":
        from mod.lib.crypto import blake3_128
        print(blake3_128(sys.argv[2]).hex())
    else:
        raise Exception(sys.argv[1])
