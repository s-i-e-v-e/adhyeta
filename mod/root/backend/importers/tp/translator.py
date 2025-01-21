from mod.lib import fs, sxml, text
from mod.lib.sxml import SxmlNode
from mod.root.backend.importers.tp import __gut_raw_base, __se_raw_base
from mod.root.backend.importers.tp import ai_translate
ds_translate = ai_translate.deepseek

def __translate_bit(xml_text: str) -> sxml.SxmlNode:
    n = sxml.from_xml(xml_text)
    xml_text = ds_translate(sxml.to_xml(n))
    try:
        return sxml.from_xml(xml_text)
    except Exception as e:
        print(e)
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~CONTINUING~~must redo this translation~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`')
        return n

def __translate_meta(doc: sxml.SxmlNode):
    meta = sxml.parse('(meta)')
    meta.append(doc.first(f"meta/title"))
    meta.append(doc.first(f"meta/author"))
    meta = __translate_bit(sxml.to_xml(meta))
    if meta.xs:
        for x in meta.xs:
            assert(isinstance(x, sxml.SxmlNode))
            if x.id == 'title':
                sxml.sxml_replace_node(doc, "/document/meta/title", x)
            if x.id == 'author':
                sxml.sxml_replace_node(doc, "/document/meta/author", x)

def __log_meta(n: sxml.SxmlNode, tokens: int):
    title = n.first("title")
    if title:
        print(f"{title.value_rec()} [{tokens}]")

def __translate_paras(ys: list[SxmlNode]):
    paras = sxml.parse('(paras)')
    paras.xs.extend(ys)
    xml_text = sxml.to_xml(paras)
    print(f"PARAS :: =<{len(ys)}> {xml_text[7:75].strip()}")
    paras = __translate_bit(xml_text)
    return paras.xs


def __write_xml_file(df: str, xml_text: str, original_title, original_author):
    fs.write_text(df, xml_text)

    try:
        doc = sxml.from_xml(fs.read_text(df))

        meta = doc.node(0)
        meta.append(sxml.parse('(note कृत्रिमबुद्ध्या कृतं भाषान्तरं इदं)'))
        if df.find('/index') != -1:
            meta.append(sxml.parse(f'(original (title {text.sxml_el_escape(original_title)})(author {text.sxml_el_escape(original_author)}))'))
            for r in doc.all("toc/ref"):
                if type(r) is str:
                    continue
                r.attrs['url'] = r.attrs['url'].replace('.xml', '.sa.xml')
        fs.write_text(df, sxml.to_xml(doc))
    except Exception as e:
        print(e)

def __get_original_meta(doc: sxml.SxmlNode):
    mx = doc.first("meta/author")
    if mx:
        original_author = mx.value()
    else:
        original_author = ''
    return doc.first("meta/title").value_rec(), original_author

TOK_MAX = 3_000
def __translate_xml_file(fp: str):
    df = fp.replace('.xml', '.sa.xml')
    if fs.exists(df):
        return
    print(f"translating {fp}")
    xml_text = fs.read_text(fp)
    doc = sxml.from_xml(xml_text)
    tokens = ai_translate.get_token_count(xml_text)
    original_title, original_author = __get_original_meta(doc)
    __log_meta(doc.node(0), tokens)
    if tokens < TOK_MAX:
        __write_xml_file(df, sxml.to_xml(__translate_bit(xml_text)), original_title, original_author)
        return

    # first translate meta
    __translate_meta(doc)
    c = doc.first("chapter")
    assert c
    xml_text = sxml.to_xml(c)
    tokens = ai_translate.get_token_count(xml_text)
    __log_meta(c, tokens)

    if tokens < TOK_MAX:
        idx = doc.xs.index(c)
        doc.xs[idx] = __translate_bit(xml_text)
    else:
        ys = []
        y_tokens = 0
        i = 0
        zs = []
        for p in c.xs:
            i += 1
            if type(p) is not SxmlNode:
                assert p == ' '
                continue

            xml_text = sxml.to_xml(p)
            tokens = ai_translate.get_token_count(xml_text)
            __log_meta(p, tokens)
            y_tokens += tokens
            if y_tokens < TOK_MAX:
                ys.append(p)
                continue

            zs.extend(__translate_paras(ys))

            ys = [p]
            y_tokens = tokens

        if y_tokens:
            zs.extend(__translate_paras(ys))
        c.xs = zs

    __write_xml_file(df, sxml.to_xml(doc), original_title, original_author)

def __fix_index(parent: str):
    index_file = f'{parent}/index.sa.xml'
    doc = sxml.from_xml(fs.read_text(index_file))

    toc = doc.node(1)
    for r in toc.xs:
        assert isinstance(r, sxml.SxmlNode)
        sf = f'{parent}/{text.sxml_attr_escape(r.attrs['url'])}'
        n = sxml.from_xml(fs.read_text(sf))
        chapter_title = n.node(0).first('title').value_rec()
        if not r.xs:
            r.xs.append('')
        r.xs[0] = chapter_title

    fs.write_text(index_file, sxml.to_xml(doc))

def __translate_dir(source_dir: str):
    print(f"translating ----- {source_dir}")
    for f in fs.list_files(source_dir):
        if not f.name.endswith(".xml") or f.name.endswith(".sa.xml"):
            continue
        __translate_xml_file(f.full_path)
    __fix_index(source_dir)

def __get_matching_dirs(parent: str, prefix: str):
    xs = []
    for x in fs.list_dirs(parent):
        if x.name.startswith(prefix):
            xs.append(x)
    return xs

def translate_se(work: str):
    if work.endswith('*'):
        for y in __get_matching_dirs(__se_raw_base(), work[:-1]):
            print(f"[*]translating {y.full_path}")
            for x in fs.list_dirs(y.full_path):
                __translate_dir(x.full_path)
    else:
        __translate_dir(__se_raw_base(work))

def translate_gut(id: str):
    if id.endswith('*'):
        for y in __get_matching_dirs(__gut_raw_base(), id[:-1]):
            print(f"[*]translating {y.full_path}")
            for x in fs.list_dirs(y.full_path):
                __translate_dir(x.full_path)
    else:
        for x in fs.list_dirs(__gut_raw_base()):
            __translate_dir(x.full_path)
