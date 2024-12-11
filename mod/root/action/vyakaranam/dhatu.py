from mod.config import env
from mod.lib import fs
from mod.lib.text import normalize
from mod.root.action.vyakaranam.sandhi import sandhi

NORMALIZED_M = normalize('ṁ')

def __to_grid(x: str) -> list[list[str]]:
    return [x.split(' ') for x in x.strip().split('\n')]

LAT_P = __to_grid("""
ti taḥ nti
si thaḥ tha
ami avaḥ amaḥ
""")

LAT_A = __to_grid("""
tē itē ntē
sē ithē dhvē
ē vahē mahē
""")

LOT_P = __to_grid("""
tu/tāt tām ntu
/tāt tam ta
ani ava ama
""")

LOT_A = __to_grid("""
tām itām ntām
sva ithām dhvam
ai avahai amahai
""")

LAN_P = __to_grid("""
t tām n
ḥ tam ta
m ava ama
""")

LAN_A = __to_grid("""
ta itām nta
thāḥ ithām dhvam
i avahi amahi
""")

VIDHI_P = __to_grid("""
it itām iyuḥ
īḥ itam ita
iyam iva ima
""")

VIDHI_A = __to_grid("""
īta īyātām īran
īthāḥ īyāthām īdhvam
īya īvahi īmahi
""")

def __classify_dhatu(xs: list[str], lakara: str, puva: str, dhatu: str, pratyaya: str):
    dhatu = normalize(dhatu)
    pratyaya = normalize(pratyaya)
    dhatu = dhatu.replace('ai', 'Q')

    ys = []
    for p in pratyaya.split('/'):
        w = dhatu + p
        w = sandhi(w)
        w = w.replace('Q', 'ai')

        x = w

        if w.endswith('m'):
            x += '/'
            x += w.rstrip('m')+NORMALIZED_M
        ys.append(x)
    xs.append('/'.join(ys))


def __rupas(xs: list[str], gss: list[list[str]], lakara: str, root: str, prefix: str = ''):
    x = f'{prefix}{root}'
    i = 1
    for gs in gss:
        j = 1
        for g in gs:
            __classify_dhatu(xs, lakara, f'{i}.{j}', x, g)
            i += 1
        j += 1

def __nama_rupas_p(xs: list[str], root: str):
    x = f'{root}n'  # pu
    x = f'{root}ntī' # str
    x = f'{root}t/{root}d'  # napu

    xs.append(x)

def __nama_rupas_a(xs: list[str], root: str):
    x = f'{root}mānaḥ'  # pu
    x = f'{root}mānā' # str
    x = f'{root}mānam' # napu
    xs.append(x)

bhvadi = fs.read_text(env.RAW_ROOT + '/vyakaranam/01-bhvadi.csv').strip().split('\n')
def __tin_sarvadhatuka(xs: list[str], no: str, root: str, final: str):
    xs.append(f"-----#{no} --- root: {root}-----")
    __rupas(xs, LAT_P, 'lat', final)
    __rupas(xs, LOT_P, 'lot', final)
    __rupas(xs, LAN_P, 'lan', final, 'a')
    __rupas(xs, VIDHI_P, 'vidhi', final)
    __nama_rupas_p(xs, final)

def __tin_sarvadhatuka_a(xs: list[str], no: str, root: str, final: str):
    xs.append(f"-----#{no} --- root: {root}-----")
    __rupas(xs, LAT_A, 'lat', final)
    __rupas(xs, LOT_A, 'lot', final)
    __rupas(xs, LAN_A, 'lan', final,'a')
    __rupas(xs, VIDHI_A, 'vidhi', final)
    __nama_rupas_a(xs, final)

def __bhvadi(xs: list[str]):
    for x in bhvadi:
        no, root, final, pada = x.split('\t')
        padas = pada.split('\\')
        finals = final.split('\\')
        for i, p in enumerate(padas):
            f = finals[i]
            if p == 'a':
                __tin_sarvadhatuka_a(xs, no, root, f)
            elif p == 'p':
                __tin_sarvadhatuka(xs, no, root, f)
            elif p == 'u':
                ff = f.split('/')
                if len(ff) == 1:
                    ff.append(ff[0])
                __tin_sarvadhatuka(xs, no, root, ff[0])
                __tin_sarvadhatuka_a(xs, no, root, ff[1])

def build_forms(xs: list[str]):
    __bhvadi(xs)