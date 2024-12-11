from mod.env import env
from mod.lib.fs import list_dirs, list_files, read_text, write_text
from mod.tool.www.publish import sxml_to_str
from mod.lib import sxml
from mod.tool.www.sxml_html import clean_html
from mod.tool.www.vfs import get_document_title

SXML_TEMPLATE = read_text("./mod/tool/www/app.sxml")
te = sxml.parse(SXML_TEMPLATE)
xx = sxml_to_str(te)

def sxml_to_html(y: sxml.SxmlNode, title: str):
    yy = sxml_to_str(y)
    html = ("<!DOCTYPE html>\n"+"".join(xx.html)
        .replace("{{main}}", "".join(yy.html))
        .replace("{{nav}}", "")
        .replace("{{title}}", f" - {title}" if title else "")
    )
    return clean_html(html)

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
        html = sxml_to_html(y, title)
        if env.IS_PRODUCTION:
            html = html.replace("/copyright.html", "https://www.adhyeta.org.in/copyright.html")
        write_text(df, html)

def run():
    sd = "./static"
    dd = env.APP_ROOT
    publish_files(sd, dd, sd, dd)