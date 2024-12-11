from mod.lib import sxml
from mod.root.action.sxml_publish_html import sxml_to_str
from mod.root.action.sxml_recognize_words import recognize_words
from mod.root.data import doc, db

def doc_to_html(loc: str, user_id: int, csrftoken: str):
    d = doc.get_by_loc(db, loc)
    assert d is not None
    text = d.text.replace("(document ", f"""(document @hx-swap none @hx-trigger "click target:a-w" @hx-post "/" @csrftoken "{csrftoken}" """)
    n = sxml.parse(text)
    sxml.move_node_to_end(n, "/document/source")
    sxml.move_node_to_end(n, "/document/copyright")
    sxml.move_node_to(n, "/document/title", 0)
    recognize_words(n, user_id)
    return sxml_to_str(n)