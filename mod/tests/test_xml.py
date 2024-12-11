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

def test_xml_2():
    a = "(doc (q hello))"
    n = sxml.parse(a)
    b = "<doc>(hello)</doc>"
    assert sxml.to_xml(n) == b

def test_prettify():
    a = '''<document>\n<meta>\n<title>TI <em>T </em> LE</title>\n</meta>\n</document>'''
    zz = '''<document>\n<meta>\n<title>TI <em>T</em> LE</title>\n</meta>\n</document>'''
    b = sxml.to_xml(sxml.from_xml(a))
    assert b == zz

def test_equality():
    a = '''<document>\n<meta>\n<title>TI <em>T </em> LE</title>\n<author>ANON</author></meta>\n<matter>\n<p>1</p><p></p>\n</matter></document>'''
    b = a.replace('\n', '')
    assert sxml.are_equal(sxml.from_xml(a), sxml.from_xml(b))

def test_multi_text_sxml():
    a = '(d h. h. munro \\(saki\\))'
    b = sxml.parse(a)
    assert len(b.xs) == 1
    assert sxml.unparse(b) == a

def test_multi_text():
    a = '<d>h. h. munro (saki)</d>'
    b = sxml.from_xml(a)
    assert len(b.xs) == 1

def test_q():
    a = '<d>(24( 7</d>'
    b = sxml.from_xml(a)

def test_roundtrip():
    a = '<d>(24( 7</d>'
    b = sxml.to_xml(sxml.parse(sxml.unparse(sxml.from_xml(a))))
    assert b == a

    a = '''(d <k> & "str"+'str'+c)'''
    b = sxml.unparse(sxml.from_xml(sxml.to_xml(sxml.parse(a))))
    assert b == a

def test_structure():
    a = '''
    <document>
        <meta>
            <title>TI T LE</title>
            <author> AN ON </author>
        </meta>
        <matter>
            <p>1 <em>emphasis</em> word <b>bold</b>word<i>italics </i> ita <strong>strong emph</strong> end </p>
            <p>A word <w>this</w>is</p>
            <p>A word<w>this</w> is</p>
            <p>A word <w>th is</w> is</p>
        </matter>
        </document>'''
    n = sxml.from_xml(a)
    assert n.id == 'document'

    meta = n.node(0)
    assert meta.id == 'meta'
    title = meta.node(0)
    assert title.value() == 'TI T LE'
    author = meta.node(1)
    assert author.value() == ('AN ON')

    matter = n.node(1)
    assert matter.id == 'matter'
    for p in matter.xs:
         assert p.id == 'p'

    p = matter.node(0)
    assert p.string(0) == '1 '
    assert p.node(1).id == 'em'
    assert p.node(1).value() == 'emphasis'
    assert p.string(2) == ' word '
    assert p.node(3).id == 'b'
    assert p.node(3).value() == 'bold'
    assert p.string(4) == 'word'
    assert p.node(5).id == 'i'
    assert p.node(5).value() == 'italics'
    assert p.string(6) == ' ita '
    assert p.node(7).id == 'strong'
    assert p.node(7).value() == 'strong emph'
    assert p.string(8) == ' end'

    p = matter.node(1)
    assert p.string(0) == 'A word '
    assert p.node(1).id == 'w'
    assert p.node(1).value() == 'this'
    assert p.string(2) == 'is'

    p = matter.node(2)
    assert p.string(0) == 'A word'
    assert p.node(1).id == 'w'
    assert p.node(1).value() == 'this'
    assert p.string(2) == ' is'

    p = matter.node(3)
    assert p.string(0) == 'A word '
    assert p.node(1).id == 'w'
    assert p.node(1).value() == 'th is'
    assert p.string(2) == ' is'

