from mod.lib import text
from mod.lib.text import strip_punctuation, list_chunks


def test_strip():
    a = "a. b: c; d!"
    b = strip_punctuation(a)
    assert " ".join(b) == "a b c d"

def test_chunks():
    xs = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26]
    assert list_chunks(xs, 5) == [[1, 2, 3, 4, 5], [6, 7, 8, 9, 10], [11, 12, 13, 14, 15], [16, 17, 18, 19, 20], [21, 22, 23, 24, 25], [26]]

def test_inclusive():
    xml = '<doc><copyright>...ab</copyright><source page="5"></source><p>133</p><p>134</p></doc>'
    piece = text.between_inclusive(xml, '<copyright>', '</source>')
    yml = text.between_inclusive_replace(xml, '<copyright>', '</source>', '<meta-info/>')
    assert yml == '<doc><meta-info/><p>133</p><p>134</p></doc>'
    assert yml.replace('<meta-info/>', piece) == xml