from dataclasses import dataclass

from mod.lib import sxml
from mod.lib.sqlite_db import Database

VirtualFS = dict[str, list[str]]

@dataclass
class State:
    db: Database
    force: bool
    last_update_ns: int


def get_document_title(n: sxml.SxmlNode):
    title = sxml.sxml_node_as_str(n, "/document/title")
    title = title if title else n.attrs["title"]
    return title