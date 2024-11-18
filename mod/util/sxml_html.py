from mod.util.sxml import SxmlNode

def render_html_node(x: SxmlNode, tag: str):
    html = ''
    if x.id == "#":
        # comment
        return html
    elif x.id in ["link", "meta", "img"]:
        o_tag = f"<{x.id}"
        c_tag = f"\n"
        html += o_tag
        if len(x.attrs):
            for k in x.attrs:
                html += f' {k}="{x.attrs.get(k)}"'
        html += f">"
    elif x.id == "\"":
        o_tag = "\u201c"
        c_tag = "\u201d"
        html += o_tag
    elif x.id == "'":
        o_tag = "\u2018"
        c_tag = "\u2019"
        html += o_tag
    elif x.id == "q":
        o_tag = f"("
        c_tag = f")"
        html += o_tag
    else :
        o_tag = f"<{x.id}"
        c_tag = f"</{x.id}>\n"

        html += o_tag
        if len(x.attrs):
            for k in x.attrs:
                if k.startswith("x-"):
                    continue
                html += f' {k}="{x.attrs.get(k)}"'
        html += f">"
    return html if tag == "B" else c_tag
