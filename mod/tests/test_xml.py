from mod.lib import sxml

doc_a = '''(document (meta (title TI&TLE) (author AUTHOR)))'''
def test_to_xml():
    a = doc_a
    b = sxml.to_xml(sxml.parse(a))
    assert b == '''<document>\n<meta>\n<title>TI&amp;TLE</title>\n<author>AUTHOR</author>\n</meta>\n</document>'''

def test_sxml_xml_round_trip():
    a = doc_a
    na = sxml.parse(a)
    xa = sxml.to_xml(na)
    nb = sxml.from_xml(xa)
    b = sxml.unparse(nb)
    assert b == doc_a.replace(') (', ')(')
    assert sxml.are_equal(na, nb)

def test_xml_11():
    a = "(doc \\(q hello\\))"
    n = sxml.parse(a)
    b = "<doc>(q hello)</doc>"
    assert sxml.to_xml(n) == b

def test_xml_2():
    a = "(doc (q hello))"
    n = sxml.parse(a)
    b = "<doc><q>hello</q></doc>"
    assert sxml.to_xml(n) == b

def test_multi_text_sxml():
    a = '(d h. h. munro \\(saki\\))'
    b = sxml.parse(a)
    assert len(b.xs) == 1
    assert sxml.unparse(b) == a

def test_roundtrip():
    a = '<d>(24( 7</d>'
    b = sxml.to_xml(sxml.parse(sxml.unparse(sxml.from_xml(a))))
    assert b == a

    a = '''(d <k> & "str"+'str'+c)'''
    b = mxl.unparse(sxml.from_xml(sxml.to_xml(sxml.parse(a))))
    assert b == a

