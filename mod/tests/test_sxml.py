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
    p = x.head()
    assert p.id == 'p'
    assert p.head() == 'This is a '
    corr = p.node(1)
    assert p.string(2) == ' book'

    sic = corr.head()
    assert sic.head() == 'god'
    assert corr.string(1) == ' good'


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
    assert p.string(0) == "abcd "
    assert p.node(1).id == "v"
    assert p.node(1).value() == "e"
    assert p.string(2) == "."

doc_b = """(document
    (title THIS IS A TITLE)
    (p (corr (sic abc) (q hello) abd.))
    (p def)
    )
    """
expected_b = """(document (title THIS IS A TITLE)(p (corr (sic abc) (q hello) abd.))(p def))"""
def test_sxml_str():
    a = doc_b
    b = sxml.unparse(sxml.parse(a))
    assert b == expected_b

    assert sxml.are_equal(
        sxml.parse(a),
        sxml.parse(b)
    )

def test_query_all():
    a = "(doc (li 1)(li 2)(li 3)(p x))"
    n = sxml.parse(a)
    xs = n.all('p')
    assert xs[0].value() == 'x'

    xs = n.all('li')
    assert xs[0].value() == '1'
    assert xs[1].value() == '2'
    assert xs[2].value() == '3'

