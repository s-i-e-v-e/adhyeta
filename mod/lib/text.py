import unicodedata
import re
from indic_transliteration import sanscript

def devanagari_to_iso(x: str):
    x = sanscript.transliterate(x, sanscript.DEVANAGARI, sanscript.ISO)
    return x

def normalize(x: str):
    return unicodedata.normalize('NFC', x)

def make_slug(title: str) -> str:
    import unicodedata
    import re
    x = devanagari_to_iso(title)
    x = unicodedata.normalize('NFD', x)
    x = x.lower()
    x = re.sub(r'\s+', '-', x)
    x = re.sub(r'[^-a-z0-9]', '', x)
    return x

delimiters = ["(", ")", "?", "!", ".", ",", ";", ":", "।", "॥", "—", "-", "/", "\u201C", "\u201D", "\u2018", "\u2019", "\t", "\n", "'", "\""]
def strip_punctuation(x: str):
    x = x.translate({ord(a): ' ' for a in delimiters})
    x = re.sub(r'\s+', ' ', x)
    x = x.strip()
    return x.split(" ")

devanagari = []
devanagari.extend(list(range(0x0902, 0x0903 + 1)))
devanagari.extend(list(range(0x0905, 0x090C + 1))) # a-r
devanagari.extend(list(range(0x090F, 0x0910 + 1))) # e-ai
devanagari.extend(list(range(0x0913, 0x0914 + 1))) # o-au
devanagari.extend(list(range(0x0915, 0x0919 + 1))) # k...
devanagari.extend(list(range(0x091A, 0x091E + 1))) # c...
devanagari.extend(list(range(0x091F, 0x0923 + 1))) # T...
devanagari.extend(list(range(0x0924, 0x0928 + 1))) # t...
devanagari.extend(list(range(0x092A, 0x092E + 1))) # p...
devanagari.extend(list(range(0x092F, 0x0930 + 1))) # y-r
devanagari.extend([0x0932, 0x0935]) # l v
devanagari.extend(list(range(0x0936, 0x0939 + 1))) # s-h
devanagari.extend(list(range(0x093D, 0x0944 + 1))) # avagraha-r
devanagari.extend(list(range(0x0947, 0x0948 + 1))) # e-ai
devanagari.extend(list(range(0x094B, 0x094C + 1))) # o-au
devanagari.extend([0x094D]) # halanta
devanagari.extend([0x0950]) # aum
devanagari.extend(list(range(0x0960, 0x0963 + 1))) # r-l-l-ll
#devanagari.extend(list(range(0x0964, 0x0965 + 1))) # danda
devanagari.extend(list(range(0x0966, 0x096F + 1))) # nos
devanagari = [chr(x) for x in devanagari]

def to_sa_words(x: str) -> list[str]:
    i = 0
    ys = []
    for xx in x:
        if len(ys) != i+1:
            ys.append("")

        if xx not in devanagari:
            i += 1
        else:
            ys[-1] += xx
    return [y for y in ys if y]
