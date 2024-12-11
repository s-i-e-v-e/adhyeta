from mod.lib import text
from mod.lib.text import make_slug

def __get_works_list(type: str, file: str):
    from mod.config import env
    from mod.lib import fs
    return [x for x in fs.read_text(f'{env.RAW_ROOT}/{type}/{file}').splitlines() if not x.startswith('#') and x.strip() != '']

def __se_work_slugs(work: str) -> tuple[str, str]:
    xs = [make_slug(x) for x in work.split('_')]
    return xs[0], xs[1]

def __se_raw_base(work = ''):
    from mod.config import env
    base = f'{env.RAW_ROOT}/standard-ebooks'
    if work:
        slug_a, slug_t = __se_work_slugs(work)
        return f'{base}/{slug_a}/{slug_t}'
    else:
        return base

def __gut_raw_base(id = ''):
    from mod.config import env
    base = f'{env.RAW_ROOT}/gutenberg'
    return f'{base}/{id}' if id else base

def __ref_to_slug(title: str, label: str, n: str):
    value = title
    value = value or (label + ' ' + n)
    return text.make_slug(value)
