import os
import shutil

def do_import(dp: str):
    do_import_ramayana(dp)
    shutil.copytree('./data/orig/śrīsubrahmaṇyabhujaṅgam', f"{dp}/śrīsubrahmaṇyabhujaṅgam")
    shutil.copytree('./data/orig/saṁskr̥tavyavahārasāhasrī', f"{dp}/saṁskr̥tavyavahārasāhasrī")

def do_import_ramayana(dp: str):
    sd = './data/orig/vālmīkirāmāyaṇam'
    dd = f'{dp}/vālmīkirāmāyaṇam'
    os.makedirs(dd, exist_ok=True)
    shutil.copyfile(os.path.join(sd, "meta.json"), os.path.join(dd, "meta.json"))
    for (k, s, x) in import_ramayana(sd):
        fn = os.path.join(dd, f"r_{k}_{s}.txt")
        with open(fn, 'w') as f:
            f.write(x)


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

def import_ramayana(sd: str):
    from mod.util.fs import read_text

    meta = [
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

    files = ['Ram01.txt', 'Ram02.txt', 'Ram03.txt', 'Ram04.txt', 'Ram05.txt', 'Ram06.txt', 'Ram07.txt']

    xs = list()
    prev_kanda = 0
    for f in files:
        fn = os.path.join(sd, f)
        prev_sarga = 0
        prev_verse = 0
        text = ''
        for x in read_text(fn).split('\n'):
            if x.startswith('%'):
                continue

            number = x[0:8]
            if not number:
                continue
            kanda = int(number[0])
            sarga = int(number[1:4])
            verse = int(number[5:7])
            pada = number[7]

            verse_text = x[9:]

            if verse != prev_verse:
                if not prev_verse:
                    pass
                else:
                    text += f" ॥{to_devanagari_no(prev_verse)}"
                    text += "\n"
                    text += "\n"
                prev_verse = verse
            else:
                text += f" ।"
                text += "\n"

            if sarga != prev_sarga:
                k = kanda - 1
                k_name = meta[k]["name"]
                k_in = meta[k]["in"]
                text = text.replace(';', '\n')
                if text:
                    text += '\n'
                    text += f"इति श्रीरामायणे {k_in} {to_ord_sarga(prev_sarga)} सर्गः ॥{to_devanagari_no(prev_sarga)}"
                    xs.append([str(kanda), str(prev_sarga).zfill(3), text])
                    text = ''

                text += f"{k_name} {to_devanagari_no(sarga)} सर्गः"
                text += "\n"
                text += "\n"
                prev_sarga = sarga

            text += verse_text

        xs[-1][2] += "\n"
        xs[-1][2] += "\n"
        xs[-1][2] += f"॥ समाप्तं {meta[prev_kanda]["name"]} ॥"
        prev_kanda += 1

    return xs
