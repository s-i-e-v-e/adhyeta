from mod.env import env
from mod.lib.fs import list_dirs, list_files, read_text, write_text
from mod.root.action.pub.html import sxml_to_html, sxml_to_str
from mod.lib import sxml
from mod.root.action.pub import get_document_title

SXML_TEMPLATE = read_text("./mod/root/action/pub/app.sxml")
te = sxml.parse(SXML_TEMPLATE)
xx = sxml_to_str(te)

def publish_files(this: str, dd: str, sd_base: str, dd_base: str):
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
        html = sxml_to_html(xx, y, title, "")
        write_text(df, html)

def run():
    sd = "./static"
    dd = env.APP_ROOT
    publish_files(sd, dd, sd, dd)