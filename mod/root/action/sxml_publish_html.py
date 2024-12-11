from dataclasses import dataclass

from mod.lib import sxml
from mod.root.action.sxml_html import render_html_node_end, render_html_node_start, clean_html

@dataclass
class Tag:
    html: list[str]
    parent: sxml.SxmlNode

def __start(x: sxml.SxmlNode|str, index: int, indent: int, q: Tag):
    if type(x) is str:
        q.html.append(x)
        return None
    elif type(x) is sxml.SxmlNode:
        if "a" in x.id and "href" in x.attrs:
            x.attrs["href"] = x.attrs["href"].replace(".sxml", ".html")
        q.html.append(render_html_node_start(x))
        return Tag(q.html, x)
    else:
        raise Exception(type(x))

def __end(x: sxml.SxmlNode|str, index: int, indent: int, q: Tag):
    if type(x) is str:
        return None
    elif type(x) is sxml.SxmlNode:
        if x.id == "source":
            if "date" in x.attrs:
                q.html.append(". ")
                q.html.append(x.attrs["date"])
            if "page" in x.attrs:
                q.html.append(". p ")
                q.html.append(x.attrs["page"])
        q.html.append(render_html_node_end(x))
        return q
    else:
        raise Exception(type(x))

def sxml_to_str(n: sxml.SxmlNode) -> str:
    q = Tag([], n)
    sxml.traverse(n, q, __start, __end)
    return "".join(q.html)

def sxml_to_html(template_html: str, y_html: str, title: str, nav: str):
    html = ("<!DOCTYPE html>\n"+template_html
        .replace("{{main}}", y_html if y_html else "{{main}}")
        .replace("{{nav}}", nav)
        .replace("{{title}}", f" - {title}" if title else "")
    )
    return clean_html(html)
