from mod.lib.sxml import SxmlNode
import re

def render_html_node_start(x: SxmlNode):
    return render_html_node(x, "B")

def render_html_node_end(x: SxmlNode):
    return render_html_node(x, "E")

def render_html_node(x: SxmlNode, tag: str):
    html = ''
    if x.id == "#":
        # comment
        return html
    elif x.id in ["link", "meta", "img", "source", "hr", "br"]:
        o_tag = f"<{x.id}"
        c_tag = ""
        html += o_tag
        if len(x.attrs):
            for k in x.attrs:
                html += f' {k}="{x.attrs.get(k)}"'
        html += ">"
    elif x.id == "\"":
        o_tag = "\u201c"
        c_tag = "\u201d"
        html += o_tag
    elif x.id == "'":
        o_tag = "\u2018"
        c_tag = "\u2019"
        html += o_tag
    elif x.id == "a-q":
        o_tag = "("
        c_tag = ")"
        html += o_tag
    else :
        o_tag = f"<{x.id}"
        c_tag = f"</{x.id}>"

        html += o_tag
        if len(x.attrs):
            for k in x.attrs:
                if k.startswith("x-"):
                    continue
                html += f' {k}="{x.attrs.get(k)}"'
        html += ">"
    return html if tag == "B" else c_tag

def clean_html(html: str):
    html = re.sub("\n+", " ", html)
    html = re.sub(" +", " ", html)
    html = re.sub("> <", "><", html)
    html = re.sub("<p>", "\n<p>", html)
    html = re.sub("</p><", "</p>\n<", html)
    html = html.strip()
    html += "\n"
    return html