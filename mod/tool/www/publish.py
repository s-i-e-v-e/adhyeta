from mod.env import env
from mod.lib.sqlite_db import Database
from mod.lib import sxml
from mod.lib.fs import copy_tree, read_text, to_file, write_text, exists, stat
from dataclasses import dataclass

from mod.lib.text import to_sa_words
from mod.tool.www.db import db_init, db_select
from mod.tool.www.sxml_html import render_html_node_end, render_html_node_start, clean_html
from mod.tool.www.vfs import State, VirtualFS, build_vfs, load_files_into_db
from mod.tool.ext.ramayana import do_import_ramayana

SXML_TEMPLATE = read_text("./mod/tool/www/www.sxml")

@dataclass
class HtmlString:
    html: list[str]
    parent: str

def to_html_start(x: sxml.SxmlNode|str, indent: int, q: HtmlString):
    if type(x) is str:
        # return whitespace as-is
        if x.strip() == '':
            q.html.append(x)
            return None
        else:
            if q.parent in ["p", "a-corr", "a-title"]:
                ys = []
                for xx in x.split(" "):
                    ys.append("<a-w>")
                    ys.append(xx)
                    ys.append("</a-w>")
                q.html.append(" ".join(ys))
            else:
                q.html.append(x)
            return None
    elif type(x) is sxml.SxmlNode:
        if "a" in x.id and "href" in x.attrs:
            x.attrs["href"] = x.attrs["href"].replace(".sxml", ".html")
        if (x.path.startswith("/document")
                and x.id not in ["a", "p", "em", "img", "hr", "ul", "li", "section", "div", "span", "form", "input", "button", "h1", "h2", "h3"]
                and not sxml.is_action(x)
                and not sxml.is_sym(x)
                ):
            x.id = f"a-{x.id}"
        q.html.append(render_html_node_start(x))
        return HtmlString(q.html, x.id)
    else:
        raise Exception(type(x))

def to_html_end(x: sxml.SxmlNode|str, indent: int, q: HtmlString):
    if type(x) is str:
            return None
    elif type(x) is sxml.SxmlNode:
        q.html.append(render_html_node_end(x))
        return q
    else:
        raise Exception(type(x))

@dataclass
class WordCount:
    ss: set[str]

def word_count_start(x: sxml.SxmlNode|str, indent: int, q: WordCount):
    if type(x) is str:
        for y in to_sa_words(x):
            q.ss.add(y)
        return None
    elif type(x) is sxml.SxmlNode:
        if x.id in ["sic", "author", "source", "copyright", "meta"]:
            return WordCount(set())
        else:
            return WordCount(q.ss)
    else:
        raise TypeError(x)

def word_count_end(x: sxml.SxmlNode|str, indent: int, q: WordCount):
    return None

def generate_files_list(db: Database, d: str):
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

def handle_list_pragma(db: Database, y: sxml.SxmlNode, floc: str):
    base_dir = sxml.get_str_node_val(y, "/document/sec/x-list")
    if base_dir:
        d = "/".join(floc.split("/")[0:-1])
        z = generate_files_list(db, d)
        sxml.replace_node(y, "/document/sec/x-list", z)

def handle_word_count(n: sxml.SxmlNode, words: set):
    q = WordCount(set())
    sxml.traverse(n, 0, q, word_count_start, word_count_end)
    unique_words = len(q.ss)
    words.update(q.ss)
    if sxml.node_exists(n, "/document/sec"):
        insert_at = "/document/category" if sxml.sxml_node_exists(n, "/document/category") else "/document/note" if sxml.sxml_node_exists(n, "/document/note") else "/document/author" if sxml.sxml_node_exists(n, "/document/author") else "/document/title"
        sxml.insert_node(n, insert_at, sxml.parse(f"(meta (p Unique Words: {unique_words}))"), 1)

def sxml_to_str(n: sxml.SxmlNode) -> HtmlString:
    xx = HtmlString([], "")
    sxml.traverse(n, 0, xx, to_html_start, to_html_end)
    return xx

def sxml_to_html(db: Database, y: sxml.SxmlNode, floc: str, title: str, bcx: str, words: set):
    xx = sxml_to_str(sxml.parse(SXML_TEMPLATE))
    handle_list_pragma(db, y, floc)
    handle_word_count(y, words)
    sxml.insert_node(y, "/document/meta", sxml.parse("(hr)"), 1)
    sxml.insert_node(y, "/document/sec", sxml.parse("(hr)"), 1)
    yy = sxml_to_str(y)

    html = ("<!DOCTYPE html>\n"+"".join(xx.html)
        .replace("{{main}}", "".join(yy.html))
        .replace("{{nav}}", bcx)
        .replace("{{title}}", f" - {title}" if title else "")
    )
    return clean_html(html)


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

def publish_files(db: Database, fs: VirtualFS, parent: str, this: str, bc: BreadCrumbs, dd: str, dd_base: str, words: set):
    if not this.endswith(".sxml"):
        bc = bc.copy()
        for x in fs[this]:
            publish_files(db, fs, this, x, bc, dd, dd_base, words)
        return
    else:
        bcx = generate_breadcrumb(bc, this.replace("/index.sxml", ""))
        for title, y, content_text, skip in db_select(db, this):
            if skip:
                continue
            if this.endswith("/index.sxml"):
                bc.append((parent if parent else "/", title))

            df = f"{dd}{this}"
            df = df.replace(".sxml", ".html")
            print(f"PUBLISHING {this} => {title} => {df}")
            html = sxml_to_html(db, y, this, title, bcx, words)
            write_text(df, html)

def run(force: bool):
    if force:
        do_import_ramayana(env.RAW_ROOT, env.SXML_TEXTS_ROOT)

    # get last publish time
    uf = f"{env.DATA_ROOT}/publish.last"
    last_update_time_ns = stat(uf).st_mtime_ns if exists(uf) else 0

    # get files updated after this time
    db = db_init()
    db.begin()

    st = State(db, force, last_update_time_ns)
    # multiple dirs separated by :
    for f in [env.SXML_TEXTS_ROOT, env.SXML_WWW_ROOT]:
        load_files_into_db(st, to_file(f))
    db.commit()
    fs = build_vfs(db)

    words = set()
    publish_files(db, fs, "", "", [], env.WWW_ROOT, env.WWW_ROOT, words)
    copy_tree("./www", env.WWW_ROOT)
    write_text(uf, "")

    # xs = list(sorted(words))
    # xs.sort()
    # write_text(f"{dd}/word.list", "\n".join(xs))

