from mod.lib.fs import list_dirs, list_files, read_text, write_text
from mod.root.action.pub.publish_as_html import sxml_to_html, sxml_to_str
from mod.lib import sxml
from mod.root.action.pub import get_document_title

from mod.root.data.repo import repo as db
TEMPLATE_HTML = sxml_to_html(sxml_to_str(None, sxml.parse(read_text("./static/app.template.sxml"))), "", "", "")

def publish_files(this: str, dd: str, sd_base: str, dd_base: str):
    if this.endswith(".template.sxml"):
        return

    if not this.endswith(".sxml"):
        for x in list_dirs(this):
            publish_files(x.full_path, dd, sd_base, dd_base)

        for x in list_files(this):
            publish_files(x.full_path, dd, sd_base, dd_base)
    else:
        df = this.replace(sd_base, dd_base).replace(".sxml", ".html")
        print(f"PUBLISHING {this} TO {df}")
        y = sxml.parse(read_text(this))
        title = get_document_title(y)
        html = sxml_to_str(None, y)
        #html = sxml_to_html(TEMPLATE_HTML, y, title, "")
        write_text(df, html)

def run(dd: str):
    sd = "./static"
    publish_files(sd, dd, sd, dd)
    write_text(f"{dd}/app.template.html", TEMPLATE_HTML)