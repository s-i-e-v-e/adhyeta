from mod.lib import sxml, text
from mod.lib.sxml import SxmlNode
import re

from mod.root.backend.importers import sxml_el
from mod.root.data import doc


def render_html_node_start(x: SxmlNode, parent: str):
    return render_html_node(x, "B", parent)

def render_html_node_end(x: SxmlNode, parent: str):
    return render_html_node(x, "E", parent)


def render_html_node(x: SxmlNode, tag: str, parent: str):
    if (x.path.startswith("/document")
            and x.id not in sxml_el.DOC_HTML_ELEMENTS
            and x.id not in sxml_el.DOC_ELEMENTS
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
                html += f' {k}="{text.xml_attr_escape(x.attrs.get(k))}"'
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


def page_has_words(n: sxml.SxmlNode, meta: doc.DocMetadata) -> bool:
    a = sxml.node_exists(n, "/document/matter")
    b = not not [x for x in ["index.sxml", "copyright.sxml", "index2.sxml"] if meta.original_loc.endswith(x)]
    return a and b

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