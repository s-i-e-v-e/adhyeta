from dataclasses import dataclass

from mod.lib import sxml
from mod.lib.sxml.traverse import ChildNodes
from mod.root.backend.importers.sxml_node_as_html import render_html_node_end, render_html_node_start, clean_html

@dataclass
class Tag:
    html: list[str]
    parent: sxml.SxmlNode

def __start(xs: ChildNodes, index: int, indent: int, q: Tag):
    x = xs[index]
    assert q is not None
    if type(x) is str:
        q.html.append(x)
        return None
    elif type(x) is sxml.SxmlNode:
        if "a" in x.id and "href" in x.attrs:
            x.attrs["href"] = x.attrs["href"].replace(".sxml", ".html")
        if x.id == "source" and "url" in x.attrs:
            x.xs[0] = sxml.parse(f'(a @href "{x.attrs["url"]}" {x.xs[0]})')
        if x.id == "narration":
            x.xs.append(sxml.parse(f'(audio @controls @src "{x.attrs["url"]}")'))
            x.xs.append('Narration: ')
            x.xs.append(x.attrs["by"])
            x.xs.append(sxml.parse(f'(br)'))
        q.html.append(render_html_node_start(x, q.parent.id))
        return Tag(q.html, x)
    else:
        raise Exception(type(x))

def __end(xs: ChildNodes, index: int, indent: int, q: Tag):
    x = xs[index]
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
        q.html.append(render_html_node_end(x, q.parent.id))
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
