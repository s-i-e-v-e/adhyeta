from mod.lib import sxml
from mod.lib.text import strip_punctuation


def test_basic():
    a = """
    (doc
    )
    """
    x = sxml.parse(a)
    assert x.id == "doc"
    assert not len(x.attrs)
    assert not len(x.xs)

def test_nested():
    a = """
    (doc
    (p
    L1
    L2
    
    L3
    
    L4
    ))
    """
    x = sxml.parse(a)
    assert x.id == "doc"
    assert not len(x.attrs)
    p = x.xs[0]
    assert p.id == "p"
    assert p.xs[0] == "L1\nL2\nL3\nL4\n"


doc_a = """
    (doc
    (p
    This is a 
    (corr (sic god) good)
  book)
    
    )
    """

def test_complex():
    x = sxml.parse(doc_a)
    assert x.id == "doc"
    p = x.xs[0]
    assert len(p.xs) == 4
    assert p.xs[0] == "This is a\n"
    assert p.xs[1].id == "corr"
    assert p.xs[2] == "\n"
    assert p.xs[3] == "book"

def test_filter():
    x = sxml.parse(doc_a)
    p, c = sxml.filter_node(x, "/doc/p/corr/sic")
    assert p and p.id == "corr"
    assert c and c.id == "sic"


doc_b = """
    (doc @id 1 @class abc)
    """

def test_attr():
    x = sxml.parse(doc_b)
    assert len(x.attrs) == 2

doc_c = """(p abcd (v e).)"""
def test_punctuation():
    p = sxml.parse(doc_c)
    assert p and p.id == "p"
    assert p.xs[0] == "abcd "
    assert p.xs[1].id == "v"
    assert p.xs[1].xs[0] == "e"
    assert p.xs[2] == "."

def test_sxml_str():
    a = """(document
    (title THIS IS A TITLE)
    (p (corr (sic abc) abd.))
    (p def)
    ) 
    """
    x = sxml.sxml_parse(a)
    b = sxml.sxml_node_as_str(x, "/document")
    expected = "THIS IS A TITLE abc abd. def"
    assert b == expected

def test_sxml_x():
    a = """(document
    (title THIS IS A TITLE)
    (p (corr (sic abc) abd.))
    (p def)
    ) 
    """
    x = sxml.sxml_parse(a)
    assert x.id == "document"

def test_strip():
    a = "a. b: c; d!"
    b = strip_punctuation(a)
    assert " ".join(b) == "a b c d"