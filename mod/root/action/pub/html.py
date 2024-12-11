from dataclasses import dataclass
from mod.lib import sxml
from mod.root.action.pub.sxml_html import render_html_node_end, render_html_node_start, clean_html

@dataclass
class HtmlString:
    html: list[str]
    parent: str

def sxml_to_html(xx: HtmlString, y: sxml.SxmlNode, title: str, nav: str):
    yy = sxml_to_str(y)
    html = ("<!DOCTYPE html>\n"+"".join(xx.html)
        .replace("{{main}}", "".join(yy.html))
        .replace("{{nav}}", nav)
        .replace("{{title}}", f" - {title}" if title else "")
    )
    return clean_html(html)

def sxml_to_str(n: sxml.SxmlNode) -> HtmlString:
    xx = HtmlString([], "")
    sxml.traverse(n, 0, xx, __to_html_start, __to_html_end)
    return xx

def __to_html_start(x: sxml.SxmlNode|str, indent: int, q: HtmlString):
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

def __to_html_end(x: sxml.SxmlNode|str, indent: int, q: HtmlString):
    if type(x) is str:
            return None
    elif type(x) is sxml.SxmlNode:
        q.html.append(render_html_node_end(x))
        return q
    else:
        raise Exception(type(x))