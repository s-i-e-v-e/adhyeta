from dataclasses import dataclass
from mod.lib import sxml
from mod.lib.sqlite_db import Database
from mod.lib.text import to_sa_words
from mod.root.data import word
from mod.root.action.pub.sxml_html import render_html_node_end, render_html_node_start, clean_html

@dataclass
class HtmlString:
    html: list[str]
    parent: str
    db: Database|None

def sxml_to_html(template_html: str, y_html: str, title: str, nav: str):
    html = ("<!DOCTYPE html>\n"+template_html
        .replace("{{main}}", y_html if y_html else "{{main}}")
        .replace("{{nav}}", nav)
        .replace("{{title}}", f" - {title}" if title else "")
    )
    return clean_html(html)

def sxml_to_str(db: Database|None, n: sxml.SxmlNode) -> str:
    xx = HtmlString([], "", db)
    sxml.traverse(n, 0, xx, __to_html_start, __to_html_end)
    return "".join(xx.html)

def __to_html_start(x: sxml.SxmlNode|str, indent: int, q: HtmlString):
    if type(x) is str:
        # return whitespace as-is
        if x.strip() == '':
            q.html.append(x)
            return None
        else:
            if q.db and q.parent in ["p", "a-corr", "a-title", "\"", "'"]:
                ys = []
                for y, w in to_sa_words(x):
                    if y:
                        ww = word.get_by_word(q.db, w)
                        if ww:
                            ys.append(f"<a-w id=\"{ww.id}\">{w}</a-w>")
                        else:
                            ys.append(f"<a-w>{w}</a-w>")
                    else:
                        ys.append(w)
                q.html.append("".join(ys))
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
        return HtmlString(q.html, x.id, q.db)
    else:
        raise Exception(type(x))

def __to_html_end(x: sxml.SxmlNode|str, indent: int, q: HtmlString):
    if type(x) is str:
            return None
    elif type(x) is sxml.SxmlNode:
        q.html.append(render_html_node_end(x))
        return q
    else:
        raise Exception(type(x))