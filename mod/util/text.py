from indic_transliteration import sanscript

def _devanagari_fix(x: str):
    INVERTED_CANDRABINDU = '\u0900'
    CANDRABINDU = '\u0901'
    ANUSVARA = '\u0902'
    VISARGA = '\u0903'

    UDATTA='\u0951'
    ANUDATTA = '\u0952'
    GRAVE = '\u0953'
    ACUTE = '\u0954'

    x = x.replace('\u0331', '\u0952')
    x = x.replace('\u030D', '\u0951')
    x = x.replace('’', 'ऽ')

    for a in [UDATTA, ANUDATTA, GRAVE, ACUTE]:
        for b in [INVERTED_CANDRABINDU, CANDRABINDU, ANUSVARA, VISARGA]:
            x = x.replace(a+b, b+a)
    return x

def hk_to_iso(x: str):
    return sanscript.transliterate(x, sanscript.HK, sanscript.ISO_VEDIC)

def iso_to_devanagari(x: str):
    x = sanscript.transliterate(x, sanscript.ISO, sanscript.DEVANAGARI)
    x = _devanagari_fix(x)
    return x

def slp1_to_devanagari(x: str):
    x = sanscript.transliterate(x, sanscript.SLP1, sanscript.DEVANAGARI)
    x = _devanagari_fix(x)
    return x
