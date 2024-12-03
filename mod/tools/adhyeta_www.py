import dataclasses
from shutil import Error
from mod.util import sxml
from mod.util.fs import copy_file, list_dirs, list_files, read_text, write_text
from mod.util.sxml import SxmlNode, sxml_get_str_node_val, sxml_parse, \
    sxml_replace_node, sxml_traverse, sxml_move_node_to_end
from mod.util.sxml_html import render_html_node
from mod.util.text import iso_to_devanagari

SXML_TEMPLATE = read_text("./mod/tools/html.sxml")

@dataclasses.dataclass
class WordCount:
    ss: set[str]
    do_translate: bool

@dataclasses.dataclass
class HtmlString:
    html: list[str]
    do_translate: bool

def to_html(x: sxml.SxmlNode|str, indent: int, q: HtmlString, tag: str):
    if type(x) == str:
        if tag == "E":
            return None

        # return whitespace as-is
        if x.strip() == '':
            q.html.append(x)
            return None
        elif q.do_translate:
            x = x.replace("..", "॥").replace(".", "।").strip(" \n")
            q.html.append(iso_to_devanagari(x))
            return None
        else:
            q.html.append(x)
            return None
    elif type(x) == sxml.SxmlNode:
        if tag == "B":
            do_trans = "x-tr" in x.attrs or x.id == "x-tr" or q.do_translate
            if "a" in x.id and "href" in x.attrs:
                x.attrs["href"] = x.attrs["href"].replace(".sxml", ".html")
            q.html.append(render_html_node(x, tag))
            return HtmlString(q.html, do_trans)
        else:
            q.html.append(render_html_node(x, tag))
            return q
    else:
        raise TypeError(f"{type(x).__name__} is not a sxml node")

def word_count(x: sxml.SxmlNode|str, indent: int, q: WordCount, tag: str):
    if type(x) == str:
        x = x.strip(" ?!;:-\"'\t\n,.\u2018\u2019\u201C\u201D।")
        if q.do_translate and x != '':
            q.ss.add(x)
        return None
    elif type(x) == sxml.SxmlNode:
        do_trans = "x-count" in x.attrs or x.id == "x-count" or q.do_translate
        return WordCount(q.ss, do_trans)
    else:
        raise TypeError(x)

def generate_files_list(d: str, base: str):
    xs = []
    xs.append("(ul")
    for f in list_files(d):
        if "index.sxml" in f:
            continue
        sf = f"{d}/{f}"
        y = sxml.sxml_parse(read_text(sf))
        if not y:
            continue
        title = sxml_get_str_node_val(y, "/document/title")
        #title = iso_to_devanagari(title)
        ff = f.replace(".sxml", ".html")
        xs.append(f"""(li (a @href "{base}/{ff}" {title}))""")
    xs.append(")")
    return sxml.sxml_parse("".join(xs))

def handle_list_pragma(y: SxmlNode, f: str):
    base_dir = sxml_get_str_node_val(y, "/document/x-list")
    if base_dir:
        d = "/".join(f.split("/")[0:-1])
        z = generate_files_list(d, base_dir)
        if z:
            sxml_replace_node(y, "/document/x-list", z)

def handle_meta_pragma(y: SxmlNode, x: SxmlNode|None):
    if x:
        sxml_replace_node(y, "/document/x-meta", x)

BreadCrumbs = list[tuple[str, str]]
def generate_breadcrumb(bc: BreadCrumbs):
    if not len(bc):
        return ""
    html = "<nav>"
    xs = []
    for uri, label in bc:
        xs.append(f"<a href='{uri}'>{label}</a>")
    html += " » ".join(xs)
    html += "</nav>"
    return html

def load_template():
    x = sxml.sxml_parse(SXML_TEMPLATE)
    xx = HtmlString([], False)
    sxml_traverse(x, 0, xx, to_html) if x else ""
    return xx

def load_document(f: str):
    q = WordCount(set(), False)
    y = sxml.sxml_parse(read_text(f).replace("-\n", ""))

    if not y:
        raise Error("file is empty")

    title = sxml_get_str_node_val(y, "/document/title")
    title = title if title else y.attrs["title"]
    #title = iso_to_devanagari(title) if title else ""

    handle_list_pragma(y, f)

    sxml_traverse(y, 0, q, word_count)
    unique_words = len(q.ss)
    handle_meta_pragma(y, sxml_parse(f"(metadata Unique Words: {unique_words})"))

    sxml_move_node_to_end(y, "/document/origin")
    sxml_move_node_to_end(y, "/document/copyright")

    yy = HtmlString([], False)
    sxml_traverse(y, 0, yy, to_html) if y else ""
    return [yy, title, y.attrs["uri"]]

def translate_sxml(f: str, pp: str, bc: BreadCrumbs):
    xx = load_template()
    yy, title, uri = load_document(f)

    bcx = generate_breadcrumb(bc)

    if f.endswith("/index.sxml"):
        bc.append((pp, title))

    return ("<!DOCTYPE html>\n"+"".join(xx.html)
            .replace("{{main}}", "".join(yy.html))
            .replace("{{nav}}", bcx)
            .replace("{{title}}", f" - {title}" if title else "")
            )


def gen(d: str, od: str, pp: str, bc: BreadCrumbs):
    pp = pp.replace("//", "/")
    bc = bc.copy()
    xs = list_files(d)
    for f in xs:
        if f == "index.sxml":
            xs.remove(f)
            xs.insert(0, f)
            break

    for f in xs:
        sf = f"{d}/{f}"
        df = f"{od}/{f}"
        if f.endswith(".sxml"):
            y = translate_sxml(sf, pp, bc)
            df = df.replace('.sxml', '.html')
            print(f"+ {df}")
            write_text(df, y)
        else:
            print(f"> {df}")
            copy_file(sf, df)

    for f in list_dirs(d):
        gen(f"{d}/{f}", f"{od}/{f}", f"{pp}/{f}", bc)

def run(dir_in: str, dir_out: str):
    gen(dir_in, dir_out, "/", [])