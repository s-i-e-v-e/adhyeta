from mod.lib import sxml

def test_basic():
    a = """
    (doc
    )
    """
    b = sxml.unparse(sxml.parse(a))
    assert b == '(doc)'

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
    b = sxml.unparse(sxml.parse(a))
    assert b == '(doc (p L1 L2 L3 L4))'


doc_a = """
    (doc
    (p
    This is a
    (corr (sic god) good)
  book)

    )
    """

def test_complex():
    b = sxml.unparse(sxml.parse(doc_a))
    assert b == '(doc (p This is a (corr (sic god) good) book))'

def test_structure():
    x = sxml.parse(doc_a)
    assert x.id == 'doc'
    p = x.xs[0]
    assert p.id == 'p'
    assert p.xs[0] == 'This is a '
    corr = p.xs[1]
    assert p.xs[2] == ' book'

    sic = corr.xs[0]
    assert sic.xs[0] == 'god'
    assert corr.xs[1] == ' good'


def test_filter():
    x = sxml.parse(doc_a)
    p, c = sxml.filter_node(x, "/doc/p/corr/sic")
    assert p and p.id == "corr"
    assert c and c.id == "sic"

def test_attr():
    a = """
        (doc @id 1 @class abc)
    """
    x = sxml.parse(a)
    assert len(x.attrs) == 2
    b = sxml.unparse(x)
    assert b == '(doc @id "1" @class "abc")'

def test_punctuation():
    a = """(p abcd (v e).)"""
    b = sxml.unparse(sxml.parse(a))
    assert b == '(p abcd (v e).)'

    p = sxml.parse(a)
    assert p and p.id == "p"
    assert p.xs[0] == "abcd "
    assert p.xs[1].id == "v"
    assert p.xs[1].xs[0] == "e"
    assert p.xs[2] == "."

doc_b = """(document
    (title THIS IS A TITLE)
    (p (corr (sic abc) (q hello) abd.))
    (p def)
    )
    """
expected_b = """(document (title THIS IS A TITLE) (p (corr (sic abc) (q hello) abd.)) (p def))"""
def test_sxml_str():
    a = doc_b
    b = sxml.unparse(sxml.parse(a))
    assert b == expected_b

    assert sxml.are_equal(
        sxml.parse(a),
        sxml.parse(b)
    )

def test_xml():
    a = doc_b
    na = sxml.parse(a)
    xa = sxml.to_xml(na)
    nb = sxml.from_xml(xa)
    b = sxml.unparse(nb)
    assert sxml.are_equal(na, nb)
    assert b == expected_b

def test_xml_2():
    a = "(doc (q hello))"
    n = sxml.parse(a)
    b = "<doc>(hello)</doc>"
    assert sxml.to_xml(n) == b