import pprint
import sys

import mod.tool.ocr as ocr
import mod.tool.uuid as uuid
from mod.lib import sxml, fs

def xml_list_unique_elements(path: str, rel_path: str = '', unique = dict(), level = 0):
    def traverse(n: sxml.SxmlNode, file_path: str):
        for c in n.list_nodes():
            traverse(c, file_path)
        if not n.id in unique:
            unique[n.id] = []
        #unique[n.id].append(file_path)

    for f in fs.list_dirs(path):
        xml_list_unique_elements(f.full_path, f.full_path.replace(path, ''), unique, level + 1)

    for f in [f for f in fs.list_files(path) if f.name.endswith('.xml')]:
        n = sxml.from_xml(fs.read_text(f.full_path))
        traverse(n, f'{rel_path}/{f.name}')

    if not level:
        pprint.pprint(unique)

def xml_checker(path: str):
    for f in fs.list_dirs(path):
        xml_checker(f.full_path)

    for f in [f for f in fs.list_files(path) if f.name.endswith('.xml')]:
        a = fs.read_text(f.full_path)
        try:
            sxml.from_xml(a)
        except:
            # try fixing translation error
            a = a.replace('</chapter>\n</document><p>', '<p>')
            try:
                sxml.from_xml(a)
                fs.write_text(f.full_path, a)
                print(f'fixed: {f.name}')
            except:
                print(f'bad: {f.name}')

def xml_prettify(path: str):
    for f in fs.list_dirs(path):
        xml_prettify(f.full_path)

    for f in [f for f in fs.list_files(path) if f.name.endswith('.xml')]:
        print(f'prettify: {f.name}')
        a = fs.read_text(f.full_path)
        a = sxml.xml_prettify(a)
        fs.write_text(f.full_path, a)

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
        from mod.root.backend.importers.tp import gut_download, se_download, ramayana
        file = sys.argv[2] if len(sys.argv) > 2 else 'work.list'
        debug = False
        se_download.process(file, debug)
        if not debug: gut_download.process(file)
        ramayana.generate(env.RAW_ROOT, env.SXML_ROOT)
    elif sys.argv[1] == "translate":
        from mod.root.backend.importers.tp import translator
        backend = sys.argv[2]
        if backend == "se":
            translator.translate_se(sys.argv[3])
        elif backend == "gut":
            translator.translate_gut(sys.argv[3])
        elif backend == "file":
            translator.translate_file(sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 0)
        else:
            print("unknown backend")
    elif sys.argv[1] == "generate":
        from mod.root.backend.importers.tp import generator
        generator.generate_se()
        generator.generate_gut()
    elif sys.argv[1] == "xml":
        path = fs.abs(sys.argv[3])
        match sys.argv[2]:
            case "check":
                xml_checker(path)
            case "pretty":
                xml_prettify(path)
            case "unique":
                xml_list_unique_elements(path)
            case _: raise Exception()
    elif sys.argv[1] == "trans-check":
        from mod.root.backend.importers.tp import doc_defective_translation
        doc_defective_translation.__find(sys.argv[2])
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
