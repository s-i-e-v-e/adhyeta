from dataclasses import dataclass

from mod.lib import sxml
from mod.lib.sxml.sxml_html import render_html_node_end, render_html_node_start, clean_html

@dataclass
class Tag:
    html: list[str]
    parent: str

HTML_ELEMENTS = ["a", "p", "em", "img", "hr", "ul", "li", "section", "div", "span", "form", "input", "button", "h1", "h2", "h3"]

def __start(x: sxml.SxmlNode|str, index: int, indent: int, q: Tag):
    if type(x) is str:
        q.html.append(x)
        return None
    elif type(x) is sxml.SxmlNode:
        if "a" in x.id and "href" in x.attrs:
            x.attrs["href"] = x.attrs["href"].replace(".sxml", ".html")
        if (x.path.startswith("/document")
                and x.id not in HTML_ELEMENTS
                and not sxml.is_action(x)
                and not sxml.is_sym(x)
                ):
            x.id = f"a-{x.id}"
        q.html.append(render_html_node_start(x))
        return Tag(q.html, x.id)
    else:
        raise Exception(type(x))

def __end(x: sxml.SxmlNode|str, index: int, indent: int, q: Tag):
    if type(x) is str:
        return None
    elif type(x) is sxml.SxmlNode:
        q.html.append(render_html_node_end(x))
        return q
    else:
        raise Exception(type(x))

def sxml_to_str(n: sxml.SxmlNode) -> str:
    q = Tag([], "")
    sxml.traverse(n, q, __start, __end)
    return "".join(q.html)

def sxml_to_html(template_html: str, y_html: str, title: str, nav: str):
    html = ("<!DOCTYPE html>\n"+template_html
        .replace("{{main}}", y_html if y_html else "{{main}}")
        .replace("{{nav}}", nav)
        .replace("{{title}}", f" - {title}" if title else "")
    )
    return clean_html(html)
