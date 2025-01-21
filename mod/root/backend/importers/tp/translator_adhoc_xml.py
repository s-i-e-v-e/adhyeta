import math
import pprint
import re

from mod.lib import fs, text, mxml

def __ds_translate(xml: str):
    from mod.root.backend.importers.tp import ai_translate
    #o_xml = ai_translate.deepseek(xml)
    o_xml = ai_translate.gemini(xml)
    if o_xml.strip().endswith('<DS-BREAK>'):
        pass
    elif not o_xml.strip().endswith('>'):
        pass
    else:
        return o_xml
    return f'<retry><ori>{xml}</ori><out>{o_xml}</out></retry>'

MAX_TOKENS = 1_024 * 4
def __translate_adhoc_file(fp: str):
    df = fp.replace('.xml', '.sa.xml')
    pf = df.replace('.xml', '.xml.part')

    xml_text = fs.read_text(fp)
    if '<copyright>' in xml_text:
        piece = text.between_inclusive(xml_text, '<copyright>', '</source>')
        xml_text = text.between_inclusive_replace(xml_text, '<copyright>', '</source>', '<meta-info/>')

    out_text = ''
    n = len(xml_text)
    nt = math.ceil(n/4)
    if n < MAX_TOKENS:
        print(f'FULLY TRANSLATING {fp} [{nt} toks]')
        out_text = __ds_translate(xml_text)
    else:
        print(f'BATCH-TRANSLATING {fp} [{nt} toks]')
        xs = xml_text.split('<p>')
        ys = ['<p>'+x for x in xs[1:]]
        ys.insert(0, xs[0])

        xx = ''
        xnnt = 0
        for y in ys:
            if len(xx) + len(y) < MAX_TOKENS:
                xx += y
            else:
                nn = len(xx)
                nnt = math.ceil(nn/4)
                print(f'==========[{xnnt} + {nnt}/{nt} toks]')
                xnnt += nnt
                out_text += __ds_translate(xx)
                fs.write_text(pf, out_text)
                xx = y
        if xx:
            nn = len(xx)
            nnt = math.ceil(nn / 4)
            print(f'==========[{xnnt} + {nnt}/{nt} toks]')
            out_text += __ds_translate(xx)

    if '<meta-info/>' in out_text:
        out_text = out_text.replace('<meta-info/>', piece)
    out_text = out_text.replace('</meta>\n<chapter>', '<note>कृत्रिमबुद्ध्या कृतं भाषान्तरं इदं</note>\n</meta>\n<chapter>')
    fs.write_text(df, out_text)
    fs.rm(pf)


def __translation_in_progress(x: str) -> bool:
    return fs.exists(x.replace('.xml', '.sa.xml')) or fs.exists(x.replace('.xml', '.sa.xml.part'))

def __collect_files_for_translation(fp: str, xs: list[str]):
    for f in fs.list_dirs(fp):
        __collect_files_for_translation(f.full_path, xs)

    for f in fs.list_files(fp):
        if not f.name.endswith(".xml"):
            continue
        if f.name.endswith(".sa.xml"):
            continue
        if f.name.endswith(".part"):
            continue
        if __translation_in_progress(f.full_path):
            continue
        if f.name == 'index.xml':
            continue
        xs.append(f.full_path)

def translate_file(path: str, split_index: int):
    MIN_FILES = 7
    xs = []
    __collect_files_for_translation(fs.abs(path), xs)
    if split_index:
        ys = text.list_chunks(xs, max(math.ceil(len(xs)/5), MIN_FILES))
        print(f'possible indices: 1-{len(ys)}')
        xs = ys[split_index-1]
    print(f'Translating {len(xs)} files:')
    for x in xs:
        print('--'+x.split('/')[-1])
    for x in xs:
        if __translation_in_progress(x):
            print(f'Skipping {x}')
            continue
        __translate_adhoc_file(x)

def __translate_lines(xs: list[str]):
    xml = '<section>\n'
    xml += '\n'.join(xs)
    xml += '\n</section>'
    o_xml = __ds_translate(xml)
    return o_xml.replace('<section>\n', '').replace('\n</section>', '')

def handle_buggy_translation(path: str):
    for f in fs.list_dirs(path):
        handle_buggy_translation(f.full_path)

    for f in fs.list_files(path):
        if not f.name.endswith(".sa.xml"):
            continue

        print(f.name)
        # load buggy translation
        buggy = fs.read_text(f.full_path)

        # get bug range
        bn = mxml.parse(buggy)
        bbb = bn.first_('chapter').first('BUGBUGBUG')
        if not bbb:
            continue
        start = int(bbb.attrs['start'])-1
        count = int(bbb.attrs['count'])

        # load lines from original
        og = fs.read_text(f.full_path.replace('.sa.xml', '.xml')).split('\n')[start:start+count]
        print('-----------------------------------THESE LINES WILL BE TRANSLATED---------------------------')
        pprint.pprint(og)
        #
        out = re.sub(r'<BUGBUGBUG[^>]+>', __translate_lines(og), buggy)
        fs.write_text(f.full_path.replace('.sa.xml', '.sa.xml.fixed'), out)