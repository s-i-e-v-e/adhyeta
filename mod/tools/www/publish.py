from os import error
import pickle
from posixpath import normcase
import re
from shutil import Error
import typing
import dataclasses

from mod.util import sxml
from mod.tools.www.repo import Database
from mod.util.text import devanagari_to_iso, normalize
from mod.util.fs import list_dirs, list_files, read_text, copy_file, write_text
from mod.util.sxml import SxmlNode, sxml_get_str_node_val, sxml_move_node_to_start, sxml_parse, \
    sxml_replace_node, sxml_traverse, sxml_move_node_to_end
from mod.util.sxml_html import render_html_node
from mod.util.text import iso_to_devanagari

db = Database()
db.init()

SXML_TEMPLATE = read_text("./mod/tools/www/html.sxml")

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
        x = x.strip(" ?!;:\"'\t\n,.\u2018\u2019\u201C॥\u201D।")
        x = x.replace("—", "-")
        xs = x.split("-")
        for y in xs:
            if q.do_translate and y != '':
                q.ss.add(y)
        return None
    elif type(x) == sxml.SxmlNode:
        do_trans = "x-count" in x.attrs or x.id == "x-count" or q.do_translate
        do_trans = do_trans and x.id != "sic"
        return WordCount(q.ss, do_trans)
    else:
        raise TypeError(x)

def generate_files_list(d: str):
    def get_files():
        dd = dict[str, str]()
        for loc, title in db.exec("SELECT loc, title FROM book WHERE loc LIKE ?", f"{d}/%"):
            if loc.endswith("/index.sxml"):
                continue
            if title:
                dd[title] = loc
        return dict(sorted(dd.items()))

    fs = get_files()
    xs = []
    xs.append("(ul")
    for title in fs:
        f = fs[title]
        ff = f.replace(".sxml", ".html")
        xs.append(f"""(li (a @href "{ff}" {title}))""")
    xs.append(")")
    return sxml.sxml_parse("".join(xs))

def handle_list_pragma(y: SxmlNode, floc: str):
    base_dir = sxml_get_str_node_val(y, "/document/x-list")
    if base_dir:
        d = "/".join(floc.split("/")[0:-1])
        z = generate_files_list(d)
        if z:
            sxml_replace_node(y, "/document/x-list", z)

def sxml_to_str(n: SxmlNode|None) -> HtmlString:
    xx = HtmlString([], False)
    sxml_traverse(n, 0, xx, to_html) if n else ""
    return xx

def sxml_to_html(y: SxmlNode, floc: str, title: str, bcx: str):
    xx = sxml_to_str(sxml_parse(SXML_TEMPLATE))
    handle_list_pragma(y, floc)
    yy = sxml_to_str(y)

    return ("<!DOCTYPE html>\n"+"".join(xx.html)
            .replace("{{main}}", "".join(yy.html))
            .replace("{{nav}}", bcx)
            .replace("{{title}}", f" - {title}" if title else "")
            )


VirtualFS = dict[str, list[str]]
BreadCrumbs = list[tuple[str, str]]

def generate_breadcrumb(bc: BreadCrumbs, current: str):
    if not len(bc):
        return ""
    html = "<nav>"
    xs = []
    for uri, label in bc:
        if uri != current:
            xs.append(f"<a href='{uri}'>{label}</a>")
    html += " » ".join(xs)
    html += "</nav>"
    return html

def publish_files(fs: VirtualFS, parent: str, this: str, bc: BreadCrumbs, dd: str):
    if not this.endswith(".sxml"):
        bc = bc.copy()
        for x in fs[this]:
            publish_files(fs, this, x, bc, dd)
            pass
        return
    else:
        bcx = generate_breadcrumb(bc, this.replace("/index.sxml", ""))
        for title, content in db.exec("SELECT title, content FROM book WHERE loc = ?", this):
            y = pickle.loads(content)
            if this.endswith("/index.sxml"):
                bc.append((parent if parent else "/", title))

            df = f"{dd}{this}"
            df = df.replace(".sxml", ".html")
            print(f"PUBLISHING {this} => {title} => {df}")
            html = sxml_to_html(y, this, title, bcx)
            write_text(df, html)

def build_vfs():
    q = VirtualFS()

    def add_to_parent(loc: str):
        def add(p: str, c: str):
            if p != c:
                q[p].append(c)

        xs = loc.split("/")
        ys = []
        pp = ""
        for x in xs:
            ys.append(x)
            yy = "/".join(ys)
            if yy not in q:
                q[yy] = []
            add(pp, yy)
            pp = yy

        ys = xs[0:-1]
        yy = "/".join(ys)
        add(yy, loc)

    for x, in db.exec("SELECT loc FROM book order by loc ASC"):
        add_to_parent(x)

    for k in q.keys():
        xs = list(set(q[k]))

        for f in xs:
            if f.endswith("/index.sxml"):
                xs.remove(f)
                xs.insert(0, f)
                break
        q[k] = xs
    return q

def load_files_into_db(sd: str, words: set):
    def handle_meta_pragma(y: SxmlNode, x: SxmlNode | None):
        if x:
            sxml_replace_node(y, "/document/x-meta", x)

    def get_file_name(title: str) -> str:
        import unicodedata
        import re
        x = devanagari_to_iso(title)
        x = unicodedata.normalize('NFD', x)
        x = x.lower()
        x = re.sub(r'\s+', '-', x)
        x = re.sub(r'[^-a-z]', '', x)
        return x

    for f in list_dirs(sd):
        load_files_into_db(f"{sd}/{f}", words)

    for f in list_files(sd):
        if not f.endswith(".sxml"):
            raise Error(f"Expected an SXML file. Found {f}")
        sf = f"{sd}/{f}"
        n = sxml_parse(normalize(read_text(sf)).replace("--", "—").replace("-\n", ""))
        n = typing.cast(SxmlNode, n)
        if not n:
            raise Error("file is empty")

        q = WordCount(set(), False)
        sxml_traverse(n, 0, q, word_count)
        unique_words = len(q.ss)
        words.update(q.ss)
        handle_meta_pragma(n, sxml_parse(f"(metadata Unique Words: {unique_words})"))

        sxml_move_node_to_end(n, "/document/origin")
        sxml_move_node_to_end(n, "/document/copyright")
        sxml_move_node_to_start(n, "/document/title")

        title = sxml_get_str_node_val(n, "/document/title")
        title = title if title else n.attrs["title"]

        loc = n.attrs["loc"]
        fn = "index.sxml" if f == "index.sxml" else f"{get_file_name(title)}.sxml"
        loc = f"{loc}/{fn}"
        loc = loc.replace("//", "/")

        db.exec("INSERT INTO book(loc, title, content) VALUES (?, ?, ?)", loc, title, pickle.dumps(n))

def run(sd: str, dd: str):
    db.begin()
    # multiple dirs separated by :
    words = set()
    for f in sd.split(":"):
        load_files_into_db(f, words)
    db.commit()
    fs = build_vfs()
    print(fs)
    publish_files(fs, "", "", [], dd)

    xs = list(sorted(words))
    xs.sort()
    write_text(f"{dd}/word.list", "\n".join(xs))
