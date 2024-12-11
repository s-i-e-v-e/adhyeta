import unicodedata
import re
from typing import Any

from indic_transliteration import sanscript
import html

def xml_attr_escape(x: str) -> str:
    return html.escape(x, True)

def xml_el_escape(x: str) -> str:
    return html.escape(x, False)

def sxml_attr_escape(x: str) -> str:
    return x.replace('"', '\\"')

def sxml_el_escape(x: str) -> str:
    # warn: assumes that the brackets are balanced
    #return x.replace('(', '(q')
    return x.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')

def normalize(x: str):
    x = unicodedata.normalize('NFD', x)
    # remove nukhta
    x = x.replace('़', '')
    return x

def devanagari_to_iso(x: str):
    x = sanscript.transliterate(x, sanscript.DEVANAGARI, sanscript.ISO)
    x = normalize(x)
    return x

def make_slug(title: str) -> str:
    import re
    x = title
    x = x.strip()
    x = devanagari_to_iso(x)
    x = x.lower() # for Roman titles
    x = re.sub(r'\s+', '-', x)
    x = x.replace('\'', '-')
    x = x.replace('?', '-')
    x = x.replace('!', '-')
    x = re.sub(r'[^-a-z0-9]', '', x)
    x = re.sub(r'-+', '-', x)
    x = x.strip('-')
    assert x
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
devanagari.extend([0x0901]) # candrabindu
devanagari.extend(list(range(0x0960, 0x0963 + 1))) # r-l-l-ll
#devanagari.extend(list(range(0x0964, 0x0965 + 1))) # danda
devanagari.extend(list(range(0x0966, 0x096F + 1))) # nos


d2x = devanagari.copy()
d2x.extend(list(range(0x0964, 0x0965 + 1))) # danda
d2x = [chr(x) for x in d2x]
d2x.extend(["—", " ", "!", "?", ",", "\n", "-", ".", "/"]) # danda

devanagari = [chr(x) for x in devanagari]

def is_sa_word(x: str):
    for xx in x:
        if xx not in d2x:
            return False, xx
    return True, ""

def to_sa_words(x: str) -> list[tuple[bool, str]]:
    ys = []
    def append(f: bool, s: str, reason: str):
        if s == '\u094d\u092f\u0903' or s == '\u0947':
            print(reason)
            print(ys[-1])
            raise Exception(x)
        ys.append((f, s))

    s = ""
    prev_is_deva = False
    for xx in x:
        if xx not in devanagari:
            if prev_is_deva:
                append(True, s, f'prev_is_deva: {xx} [{hex(ord(xx))}]')
                s = ""
            s += xx
            prev_is_deva = False
        else:
            if not prev_is_deva:
                append(False, s, 'prev_is_not_deva')
                s = ""
            s += xx
            prev_is_deva = True

    append(prev_is_deva, s, 'DONE')

    return ys

def from_json(x: str) -> dict[str, str]:
    import json
    return json.loads(x)

def to_json(x: Any) -> str:
    import json
    return json.dumps(x)

def list_chunks(xs: list, size: int):
    ys = []
    for i in range(0, len(xs), size):
        ys.append(xs[i:i + size])
    return ys


def roman_to_int(s: str) -> int:
    # Mapping of Roman numerals to their integer values
    roman_to_int_map = {
        'I': 1,
        'V': 5,
        'X': 10,
        'L': 50,
        'C': 100,
        'D': 500,
        'M': 1000
    }

    total = 0
    prev_value = 0

    # Iterate through the Roman numeral string in reverse
    for char in reversed(s.upper()):
        current_value = roman_to_int_map[char]

        # If the current value is less than the previous value, subtract it
        if current_value < prev_value:
            total -= current_value
        else:
            total += current_value

        prev_value = current_value

    return total

def is_roman(s: str) -> bool:
    for a in s:
        if a not in 'IVXLCDM':
            return False
    return True

def between_inclusive(x: str, a: str, b: str) -> str:
    start = x.find(a)
    end = x.find(b)
    if start >= 0 and end >= 0:
        return x[start:end+len(b)]
    raise Exception()

def between_inclusive_replace(x: str, a: str, b: str, y: str) -> str:
    start = x.find(a)
    end = x.find(b)
    if start >= 0 and end >= 0:
        return x[0:start]+y+x[end+len(b):]
    raise Exception()