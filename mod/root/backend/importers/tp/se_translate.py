from math import ceil

from mod.config import env
from mod.lib import sxml, fs
from mod.lib.text import make_slug, list_chunks
from mod.raw.se_import import SE_RAW_DIR


def __translate(text: str):
    DEBUG = 0
    if DEBUG:
        n = sxml.parse(text)
        for x in n.xs:
            if type(x) is sxml.SxmlNode:
                x = sxml.as_node(x)
                x.attrs['translated'] = '1'
        return sxml.unparse(sxml.from_xml(sxml.to_xml(n)))
    else:
        from mod.raw.deepseek import translate
        xml_text = sxml.to_xml(sxml.parse(text))
        print("==========================================================")
        print(xml_text)
        print("----------------------------------------------------------")
        x = translate(xml_text)
        print(x)
        sxml_text = sxml.unparse(sxml.from_xml(x))
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print(sxml_text)
        return sxml_text

def __translate_doc(text: str):
    n = sxml.parse(text)
    title = sxml.as_node(sxml.filter_node(n, "/document/title")[1])
    _, q = sxml.filter_node(n, "/document/matter/article")
    if not q:
        _, q = sxml.filter_node(n, "/document/matter/section")
    if not q:
        _, q = sxml.filter_node(n, "/document/matter")

    matter = sxml.as_node(q)
    assert matter.id in ['matter', 'article', 'section']

    tokens = int(n.attrs.get('tokens', '1'))
    paras = len(matter.xs)
    runs = ceil(tokens / 2200)
    run_paras = ceil(paras / runs)

    ys = []
    i = 1
    pid = 1
    for xs in list_chunks(matter.xs, run_paras):
        print(f"run {i}/{runs}")
        i += 1
        xx = "(doc "
        xx += sxml.unparse(title)
        for x in xs:
            if type(x) is sxml.SxmlNode:
                x.attrs['pid'] = str(pid)
                pid += 1
            xx += sxml.unparse(x)
        xx += ")"
        xx = __translate(xx)
        nx = sxml.parse(xx)
        title = sxml.as_node(nx.xs[0])
        ys.extend(nx.xs[1:])

    for i in range(0, len(matter.xs)):
        if type(matter.xs[i]) is sxml.SxmlNode:
            z = sxml.as_node(sxml.parse("(p (tran)(orig))"))
            z.xs[1] = matter.xs[i]
            z.xs[1].id = 'orig'
            for y in ys:
                if type(y) is sxml.SxmlNode:
                    if y.attrs['pid'] == matter.xs[i].attrs['pid']:
                        ys.remove(y)
                        z.xs[0] = y
                        z.xs[0].id = 'tran'
                        y.attrs.pop('pid')
                        matter.xs[i].attrs.pop('pid')
                        break
            matter.xs[i] = z
    sxml.replace_node(n, "/document/title", title)

    return sxml.unparse(n)

def translate_work(work: str):
    author, title = work.split('_')
    slug_a = make_slug(author)
    slug_t = make_slug(title)
    source_dir = f"{SE_RAW_DIR}/{slug_a}/{slug_t}"
    dest_dir = f"{env.SXML_ROOT}/sa/k/{slug_a}/{slug_t}"
    for f in fs.list_files(source_dir):
        df = f"{dest_dir}/{f.name}"
        if fs.exists(df):
            continue
        print(f"translating {f.name} => {dest_dir}/{f.name}")
        doc = fs.read_text(f.full_path)
        if f.name == 'index.sxml':
            content = __translate(doc)
        else:
            content = __translate_doc(doc)
        fs.write_text(df, content)

def dump_work(work: str):
    author, title = work.split('_')
    slug_a = make_slug(author)
    slug_t = make_slug(title)
    source_dir = f"{SE_RAW_DIR}/{slug_a}/{slug_t}"
    dest_dir = f"/tmp/standard-ebooks/sa/k/{slug_a}/{slug_t}"
    for f in fs.list_files(source_dir):
        df = f"{dest_dir}/{f.name}"
        if fs.exists(df):
            continue
        print(f"translating {f.name} => {dest_dir}/{f.name}")
        doc = fs.read_text(f.full_path)
        content = sxml.to_xml(sxml.parse(doc))
        fs.write_text(df, content)