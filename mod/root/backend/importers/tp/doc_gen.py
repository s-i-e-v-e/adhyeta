import dataclasses


@dataclasses.dataclass
class Document:
    a: str



def replace_z3998(t: str, x: str) -> str:
    return x.replace('z3998:'+t, '')

def parse_se_doc(xml: str):
    # replace all the irrelevant z3998 references
    xml = xml.replace('z3998:name-title', '')
    xml = xml.replace('z3998:fiction', '')
    xml = xml.replace('z3998:personal-name', '')


    xml = xml.replace('z3998:verse', 'verse')