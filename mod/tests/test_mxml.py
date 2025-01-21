import pprint
from mod.lib import mxml

pretty = mxml.Prettifier.build('title author p', 'document meta matter')

def test_mxml_parse():
    a = '<document id="x" data-uuid="..."><p> An <em>apple</em>a day keeps<b>the <i>doctor</i> </b>away.</p> </document>'
    n = mxml.parse(a)
    assert n.id == 'document'
    assert n.attrs['id'] == 'x'
    assert n.attrs['data-uuid'] == '...'
    assert n.xs[0].id == 'p'

def test_mxml_prettify():
    a = '''<document>\n<meta>\n<title>TI <em>T </em> LE</title>\n</meta>\n</document>'''
    zz = '''<document><meta><title>TI <em>T</em> LE</title></meta></document>'''
    yy = '''<document>\n<meta>\n<title>TI <em>T</em> LE</title>\n</meta>\n</document>'''
    assert mxml.unparse(mxml.parse(a, pretty)) == zz
    assert mxml.unparse(mxml.parse(a, pretty), pretty) == yy

def test_mxml_equality():
    a = '''<document>\n<meta>\n<title>TI <em>T </em> LE</title>\n<author>ANON</author></meta>\n<matter>\n<p>1</p><p></p>\n</matter></document>'''
    b = a.replace('\n', ' ').replace('<em>T </em>', '<em>T</em>')
    assert mxml.parse(a, pretty) == mxml.parse(b, pretty)

def test_mxml_multi_text():
    a = '<d>h. h. munro (saki)</d>'
    b = mxml.parse(a)
    assert len(b.xs) == 1

def test_mxml_q():
    a = '<d>(24( 7</d>'
    b = mxml.parse(a)

def test_mxml_structure():
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
    n = mxml.parse(a)
    assert n.id == 'document'

    meta = n.first_('meta')
    title = meta.first_('title')
    assert title.value() == 'TI T LE'
    author = meta.first_('author')
    assert author.value() == ('AN ON')

    matter = n.first_('matter')
    for p in matter.list_nodes():
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

    p = matter.node(2)
    assert p.string(0) == 'A word '
    assert p.node(1).id == 'w'
    assert p.node(1).value() == 'this'
    assert p.string(2) == 'is'

    p = matter.node(4)
    assert p.string(0) == 'A word'
    assert p.node(1).id == 'w'
    assert p.node(1).value() == 'this'
    assert p.string(2) == ' is'

    p = matter.node(6)
    assert p.string(0) == 'A word '
    assert p.node(1).id == 'w'
    assert p.node(1).value() == 'th is'
    assert p.string(2) == ' is'
