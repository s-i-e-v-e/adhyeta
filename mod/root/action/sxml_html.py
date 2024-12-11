from html import escape
from mod.lib import sxml
from mod.lib.sxml import SxmlNode
import re

def render_html_node_start(x: SxmlNode):
    return render_html_node(x, "B")

def render_html_node_end(x: SxmlNode):
    return render_html_node(x, "E")

DOC_HTML_ELEMENTS = ["a", "p", "em", "img", "ul", "li", "section", "div", "span", "form", "input", "button", "h1", "h2", "h3", "link", "img", "hr", "br", "ruby","rt"]
DOC_ELEMENTS = ["q", "w", "n", "v", "g", "t", "lit", "sec", "document", "copyright", "author", "note", "category", "corr", "sic"]
def render_html_node(x: SxmlNode, tag: str):
    if (x.path.startswith("/document")
            and x.id not in DOC_HTML_ELEMENTS
            and not x.id in DOC_ELEMENTS
            and not sxml.is_action(x)
            and not sxml.is_sym(x)
    ):
        rid = f"a-{x.id}"
    else:
        rid = x.id

    html = ''
    if rid == "#":
        # comment
        return html
    elif rid in ["link", "img", "hr", "br", "meta", "source"]:
        o_tag = f"<{rid}"
        c_tag = ""
        html += o_tag
        if len(x.attrs):
            for k in x.attrs:
                html += f' {k}="{x.attrs.get(k)}"'
        html += ">"
    elif rid == "\"":
        o_tag = "\u201c"
        c_tag = "\u201d"
        html += o_tag
    elif rid == "'":
        o_tag = "\u2018"
        c_tag = "\u2019"
        html += o_tag
    elif rid == "q":
        o_tag = "("
        c_tag = ")"
        html += o_tag
    else :
        o_tag = f"<{rid}"
        c_tag = f"</{rid}>"

        html += o_tag
        if len(x.attrs):
            for k in x.attrs:
                if k.startswith("x-"):
                    continue
                html += f' {k}="{escape(x.attrs.get(k), True)}"'
        html += ">"
    return html if tag == "B" else c_tag

def clean_html(html: str):
    html = re.sub("\n+", " ", html)
    html = re.sub(" +", " ", html)
    #html = re.sub("> <", "><", html)
    html = re.sub("<p>", "\n<p>", html)
    html = re.sub("</p><", "</p>\n<", html)
    html = html.strip()
    html += "\n"
    return html


BreadCrumbs = list[tuple[str, str]]

def generate_breadcrumb(bc: BreadCrumbs, current: str):
    if not len(bc):
        return ""
    html = """<nav id="crumbs">"""
    xs = []
    for uri, label in bc:
        if uri != current:
            xs.append(f"<a href='{uri}'>{label}</a>")
    html += " » ".join(xs)
    html += "</nav>"
    return html