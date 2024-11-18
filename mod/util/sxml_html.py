from typing import Callable

from mod.util import sxml


def sxml_to_html(x: sxml.List, fn: Callable[[sxml.List, str], str]):
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>sxml -> html</title>
        <style>
            * {
                font-family: Shobhika;
            }
            h {
                display: block;
                font-weight: bold;
            }
        </style>
    <head>
    <body>
    """+_build(x, 0, fn)+"""</body></html>"""

def _build(x: sxml.List, indent: int, fn: Callable[[sxml.List, str], str]):
    html = ''

    c_tag = ''
    if x.id in ["p", "h", "title", "document"]:
        o_tag = f"<{x.id}"
        c_tag = f"</{x.id}>\n"

        html += o_tag
        if len(x.attrs):
            for k, v in x.attrs:
                html += f' {k}="{v}"'
        html += f">"
    elif x.id == "'":
        o_tag = f"("
        c_tag = f")"
        html += o_tag
    elif x.id == "#":
        # comment
        return ''

    yy = ''
    for v in x.xs:
        if type(v) is str:
            yy += fn(x, v)
        else:
            yy += _build(v, indent + 1, fn)

    html += yy.strip()
    html += c_tag
    return html