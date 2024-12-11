# two kinds of dhātus
# - aupadēśika
# - ātidēśika
#
# aupadēśika
# - 1930 dhātus divided into 10 gaṇās
# - categorization only useful for sārvadhutaka pratyayas
# - not relevant for ārdhadhutaka pratyayas
#
# ātidēśika
# - formed out of 12 sanādi pratyayas
#
# both kinds can have the following pratyayas
# - tiṅ
# - kr̥t
#
# both pratyayas can be further divided into
# - sārvadhutaka
# - ārdhadhutaka
#
# of the tiṅ pratyayas
# - sārvadhutaka: lat lōt laṅg vidhiliṅg
# - ārdhadhutaka: rest
#
# of the kr̥t pratyayas
# - sārvadhutaka: śatr̥ śānac
# - ārdhadhutaka: rest
#
from mod.lib.text import normalize

def reverse(xs: list) -> list:
    xs.reverse()
    return xs

AC = reverse('a ā i ī u ū r̥ r̥̄ lr̥ lr̥̄ ē ai ō au'.split(' '))
AK = reverse('a ā i ī u ū r̥ r̥̄ lr̥ lr̥̄'.split(' '))
IK = reverse('i ī u ū r̥ r̥̄ lr̥ lr̥̄'.split(' '))
EC = reverse('ē ai ō au'.split(' '))


def __yan_sandhi():
    xs = []
    adesha = reverse('y y v v r r l l'.split(' '))
    for i, x in enumerate(IK):
        for y in AC:
           xs.append((x+y, adesha[i]))
    return xs

def __ayadi_sandhi():
    xs = []
    adesha = reverse('ay āy av āv'.split(' '))
    for i, x in enumerate(EC):
        for y in AC:
           xs.append((x+y, adesha[i]))
    return xs

def __savarna_dirgha_sandhi():
    xs = []
    adesha = reverse('ā ā ī ī ū ū r̥̄ r̥̄ lr̥̄ lr̥̄'.split(' '))
    for i, x in enumerate(AK):
        n = i if i % 2 == 0 else i-1
        for y in [AK[n], AK[n+1]]:
            xs.append((x+y, adesha[i]))
    return xs

def __guna_sandhi():
    xs = []
    adesha = reverse('ē ē ō ō ar ar al al'.split(' '))
    for x in reverse('a ā'.split(' ')):
        for i, y in enumerate(IK):
           xs.append((x+y, adesha[i]))
    return xs

def __vrddhi_sandhi():
    xs = []
    adesha = reverse('ai ai au au'.split(' '))
    for x in reverse('a ā'.split(' ')):
        for i, y in enumerate(EC):
           xs.append((x+y, adesha[i]))
    return xs

def __sandhi_table():
    xs = []
    xs.extend(__savarna_dirgha_sandhi())
    xs.extend(__guna_sandhi()) # some exceptions for ajadi lang lakara forms
    xs.extend(__vrddhi_sandhi())
    xs.extend(__yan_sandhi())
    xs.extend(__ayadi_sandhi())
    # todo - para-rupa, purva-rupa
    return [(normalize(x), normalize(y)) for x, y in xs]

SANDHI = __sandhi_table()


def sandhi(w: str):
    for idx, (x, y) in enumerate(SANDHI):
        # if normalize('aī') in w:
        #     print(f"{idx}: {w} -- {w.replace(x, y)} == {x} --  {y}")
        w = w.replace(x, y)
    return w
