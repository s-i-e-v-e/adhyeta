import re
from dataclasses import dataclass

from mod.lib import fs
from mod.lib.text import make_slug
from mod.root.backend.importers.tp.project_uuids import get_uuids_for_work

def to_devanagari_no(n: int):
    nos = [
        "०",
        "१",
        "२",
        "३",
        "४",
        "५",
        "६",
        "७",
        "८",
        "९"
    ]

    y = ''
    for x in str(n):
        y += nos[int(x)]
    return y

def to_ord_sarga(n: int):
    nos = [
        "",
        "प्रथमः",
        "द्वितीयः",
        "तृतीयः",
        "चतुर्थः",
        "पञ्चमः",
        "षष्ठः",
        "सप्तमः",
        "अष्टमः",
        "नवमः",
        "दशमः",
        "एकादशः",
        "द्वादशः",
        "त्रयोदशः",
        "चतुर्दशः",
        "पञ्चदशः",
        "षोडशः",
        "सप्तदशः",
        "अष्टादशः",
        "नवदशः",
        "विंशतितमः",
        "एकविंशतितमः",
        "द्वाविंशतितमः",
        "त्रयोविंशतितमः",
        "चतुर्विंशतितमः",
        "पञ्चविंशतितमः",
        "षड्विंशतितमः",
        "सप्तविंशतितमः",
        "अष्टाविंशतितमः",
        "एकोनत्रिंशत्तमः",
        "त्रिंशत्तमः",
        "एकत्रिंशत्तमः",
        "द्वात्रिंशत्तमः",
        "त्रयस्त्रिंशः",
        "चतुस्त्रिंशः",
        "पञ्चत्रिंशः",
        "षट्त्रिंशः",
        "सप्तत्रिंशः",
        "अष्टत्रिंशः",
        "एकोनचत्वारिंशः",
        "चत्वारिंशः",
        "एकचत्वारिंशः",
        "द्विचत्वारिंशः",
        "त्रिचत्वारिंशः",
        "चतुश्चत्वारिंशः",
        "पञ्चचत्वारिंशः",
        "षट्चत्वारिंशः",
        "सप्तचत्वारिंशः",
        "अष्टचत्वारिंशः",
        "एकोनपञ्चाशः",
        "पञ्चाशः",
        "एकपञ्चाशः",
        "द्विपञ्चाशः",
        "त्रिपञ्चाशः",
        "चतुःपञ्चाशः",
        "पञ्चपञ्चाशः",
        "षट्पञ्चाशः",
        "सप्तपञ्चाशः",
        "अष्टपञ्चाशः",
        "एकोनषष्टितमः",
        "षष्टितमः",
        "एकषष्टितमः",
        "द्विषष्टितमः",
        "त्रिषष्टितमः",
        "चतुष्षष्टितमः",
        "पञ्चषष्टितमः",
        "षट्षष्टितमः",
        "सप्तषष्टितमः",
        "अष्टषष्टितमः",
        "एकोनसप्ततितमः",
        "सप्ततितमः",
        "एकसप्ततितमः",
        "द्वासप्ततितमः",
        "त्रिसप्ततितमः",
        "चतुस्सप्ततितमः",
        "पञ्चसप्ततितमः",
        "षट्सप्ततितमः",
        "सप्तसप्ततितमः",
        "अष्टासप्ततितमः",
        "एकोनाशीतितमः",
        "अशीतितमः",
        "एकाशीतितमः",
        "द्व्यशीतितमः",
        "त्र्यशीतितमः",
        "चतुरशीतितमः",
        "पञ्चाशीतितमः",
        "षडशीतितमः",
        "सप्ताशीतितमः",
        "अष्टाशीतितमः",
        "एकोननवतितमः",
        "नवतितमः",
        "एकनवतितमः",
        "द्विनवतितमः",
        "त्रिनवतितमः",
        "चतुर्नवतितमः",
        "पञ्चनवतितमः",
        "षण्णवतितमः",
        "सप्तनवतितमः",
        "अष्टानवतितमः",
        "नवनवतितमः",
        "शततमः",
        "एकोत्तरशततमः",
        "द्व्यधिकशततमः",
        "त्र्यधिकशततमः",
        "चतुरधिकशततमः",
        "पञ्चाधिकशततमः",
        "षडधिकशततमः",
        "सप्ताधिकशततमः",
        "अष्टोत्तरशततमः",
        "नवोत्तरशततमः",
        "दशोत्तरशततमः",
        "एकादशाधिकशततमः",
        "द्वादशोत्तरशततमः",
        "त्रयोदशाधिकशततमः",
        "चतुर्दशाधिकशततमः",
        "पञ्चदशाधिकशततमः",
        "षोडशोत्तरशततमः"
    ]
    return nos[n]

def to_kanda(n: int):
    kandas = [
        {
            "name": "बालकाण्डम्",
            "in": "बालकाण्डे"
        },
        {
            "name": "अयोध्याकाण्डम्",
            "in": "अयोध्याकाण्डे"
        },
        {
            "name": "अरण्यकाण्डम्",
            "in": "अरण्यकाण्डे"
        },
        {
            "name": "किष्किन्धाकाण्डम्",
            "in": "किष्किन्धाकाण्डे"
        },
        {
            "name": "सुन्दरकाण्डम्",
            "in": "सुन्दरकाण्डे"
        },
        {
            "name": "युद्धकाण्डम्",
            "in": "युद्धकाण्डे"
        },
        {
            "name": "उत्तरकाण्डम्",
            "in": "उत्तरकाण्डे"
        }
    ]
    k = kandas[n-1]
    return k["name"], k["in"]

@dataclass
class Pada:
    id: str
    text: str

def generate_sxml(sd: str, dd: str):
    def set_data(dx: dict, x: str):
        kanda = int(x[0])
        sarga = int(x[1:4])
        verse = int(x[5:7])

        ps = x[9:].split(';')

        if kanda not in dx:
            dx[kanda] = {}
        sx = dx[kanda]

        if sarga not in sx:
            sx[sarga] = {}
        vx = sx[sarga]

        if verse not in vx:
            vx[verse] = []

        ys = vx[verse]

        for i in range(0, len(ps)):
            p = chr(i+ord(x[7:8]))
            ys.append(Pada(p, ps[i]))

    # consolidate
    xs = list()
    for f in fs.list_files(sd)[1:]:
        if not f.name.endswith('.txt'):
            continue
        for x in fs.read_text(f.full_path).split('\n'):
            if not x or x.startswith('%'):
                continue
            xs.append(x)

    dx = dict[int, dict[int, dict[int, list[Pada]]]]()
    for x in xs:
        set_data(dx, x)

    uuids = get_uuids_for_work(f'{sd}/ids')
    fs.write_text(f"{dd}/index.sxml", get_kanda_list(uuids))
    for kanda in dx.keys():
        xss = dx[kanda].keys()
        k_name, k_in = to_kanda(kanda)

        fs.write_text(f"{dd}/{kanda}/index.sxml", get_sarga_list(uuids, kanda, k_name, list(xss)))

        for s, sarga in enumerate(xss):
            sarga_label = str(sarga).zfill(3)
            ys = []
            ys.append(f"""
                (document @uuid {uuids.pop()} @loc "/sa/itihasa/{title_slug}/{kanda}/{sarga_label}.sxml"
                (meta
                (copyright CC0. No rights reserved)
                (source "{title} Baroda Critical Edition")
                (title {to_devanagari_no(sarga)} सर्गः)
                )
                (matter
            """)

            xvs = dx[kanda][sarga].keys()
            for v, verse in enumerate(xvs):
                ys.append(f"""
                (p @id "{kanda}.{sarga}.{verse}"
                """)

                xps = dx[kanda][sarga][verse]

                is_split = len(xps) > 2 and [x for x in xps if x.id in ["b", "d", "f", "h"]]
                for p, y in enumerate(xps):
                    ys.append(f"""(v {y.text}""")
                    if p == len(xps) - 1:
                        ys.append(f"॥ {to_devanagari_no(verse)}))\n")
                    else:
                        if is_split:
                            if y.id in ["b", "d", "f", "h"]:
                                ys.append("।)\n")
                            else:
                                ys.append(")\n")
                        else:
                            ys.append("।)\n")

            ys.append(f"""
                (p (v इति श्रीरामायणे {k_in} {to_ord_sarga(sarga)} सर्गः ॥ {to_devanagari_no(sarga)}))
            """)

            if s == len(xss) - 1:
                k_name, k_in = to_kanda(kanda)
                ys.append(f"""
                    (p (v ॥ समाप्तं {k_name} ॥))
                """)

            ys.append("))\n")
            yy = "".join(ys).replace('\t', ' ')
            yy = re.sub(r" *\n *", "\n", yy).strip()
            yy += "\n"

            fs.write_text(f"{dd}/{kanda}/{sarga_label}.sxml", yy)

title = "वाल्मीकिरामायणम्"
title_slug = make_slug(title)+'-bce'

def get_sarga_list(uuids: list[str], k: int, k_name: str, xs: list[int]):
    ys = []
    ys += f"""
(document @uuid {uuids.pop()}
(meta
(copyright CC0. No rights reserved)
(source "{title} Baroda Critical Edition")
(title {k_name})
)
(matter
(p
""".strip()
    for s in xs:
        ys += f"""(lit (a @href "/sa/itihasa/{title_slug}/{k}/{str(s).zfill(3)}.sxml" सर्गः {to_devanagari_no(s)}))"""
    ys += ")))"
    return "".join(ys)

def get_kanda_list(uuids: list[str]):
    ys = []
    ys += f"""
(document @uuid {uuids.pop()}
(meta
(copyright CC0. No rights reserved)
(source "{title} Baroda Critical Edition")
(title {title} BCE)
)
(matter
(p
""".strip()
    for k in range(1, 7+1):
        k_name, k_in = to_kanda(k)
        ys += f"""(lit (a @href "/sa/itihasa/{title_slug}/{k}/" {k_name}))"""
    ys += ")))"
    return "".join(ys)

def generate(raw_dir: str, texts_dir: str):
    sd = f'{raw_dir}/bombay.indology.info/valmikiramayanam-bce'
    dd = f'{texts_dir}/sa/itihasa/{title_slug}/'

    generate_sxml(sd, dd)