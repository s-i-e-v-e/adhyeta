from mod.lib import fs
from mod.root.action.sxml_publish_html import sxml_to_html, sxml_to_str
from mod.lib import sxml

TEMPLATE_HTML = sxml_to_html(sxml_to_str(sxml.parse(fs.read_text("./static/app.template.sxml"))), "", "", "")

def publish_files(this: str, dd: str, sd_base: str, dd_base: str):
    if this.endswith(".template.sxml"):
        return

    if not this.endswith(".sxml"):
        for x in fs.list_dirs(this):
            publish_files(x.full_path, dd, sd_base, dd_base)

        for x in fs.list_files(this):
            publish_files(x.full_path, dd, sd_base, dd_base)
    else:
        df = this.replace(sd_base, dd_base).replace(".sxml", ".html")
        print(f"PUBLISHING {this} TO {df}")
        y = sxml.parse(fs.read_text(this))
        html = sxml_to_str(y)
        fs.write_text(df, html)

def run(dd: str):
    sd = "./static"
    publish_files(sd, dd, sd, dd)
    fs.write_text(f"{dd}/app.template.html", TEMPLATE_HTML)