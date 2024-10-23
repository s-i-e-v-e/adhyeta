from mod.repo.works import part_load, word_get, works_list_all, parts_list_all, word_status_toggle, word_note_set, \
    work_load, get_word_stats


def work_list_page_render():
    html = ""
    html += """<div hx-push-url="true">"""
    html += """<ul>"""
    for [id, name] in works_list_all():
        url=f"/e/work/{id}"
        html += f"""<li><a hx-target="main" hx-get="{url}" href="{url}">{name}</a></li>"""

    html += """</ul>"""
    html += """</div>"""
    return html

def work_parts_list_page_render(work_id: int):
    ys = parts_list_all(work_id)
    zs = get_word_stats(work_id)
    if len(ys) > 1:
        [_, work_name] = work_load(work_id)
        html = ""
        html += """<div hx-push-url="true">"""
        html += f"<h3>{work_name}</h3>"
        html += """<ul>"""
        for [xx, yy] in zip(ys, zs):
            (part_id, name) = xx
            (a, b) = yy
            url = f"/e/work/{work_id}/part/{part_id}"
            html += f"""<li><a hx-target="main" hx-get="{url}" href="{url}">{name}</a>[{a}/{b}]</li>"""
        html += """</ul>"""
        html += """</div>"""
        return html
    else:
        return part_page_render(work_id, ys[0][0], 0, "", "")

def part_page_render(work_id: int, part_id: int, w: int, trigger: str, note: str):
    url = f"/e/work/{work_id}/part/{part_id}"
    if w:
        if trigger == "c":
            word_status_toggle(w)
        elif trigger == "a+c":
            html = __note_render(url, w)
            return html
        else:
            word_note_set(w, note)

    else:
        pass

    xs = part_load(part_id)
    [_, work_name] = work_load(work_id)
    html = ""
    html += f"<h3>{work_name}</h3>"
    html += """<div class="content">"""
    n = 0
    for [word_id, w, is_known, ignore, line_no, word_no, _note] in xs:
        n = line_no if n == 0 else n
        if w == '\n':
            html += """<p><br>"""
        else:
            if n != line_no:
                html += """<p>"""
                n = line_no

            html += __word_render(url, word_id, w, _note, is_known, ignore, __uid(line_no, word_no))
    html += "</div>"
    return html

def __uid(line_no: int, word_no: int):
    return f"w_{line_no}_{word_no}"

def __word_render(url: str, word_id: int, w: str, note: str, is_known: bool, ignore: bool, uid: str):
    html = ""

    if ignore:
        html += w
    else:
        w_is_known = "is-k" if is_known else ""

        html_note = ""
        if note:
            html_note += f"<x-n>{note.replace('\n', '<br>')}</x-n>"

        html += f"""<x-wc id="{uid}" {w_is_known}>
            {html_note}
            <x-w hx-put="{url}" x-w-id="{word_id}" hx-trigger="click">
            <x-w hx-put="{url}" x-w-id="{word_id}" hx-target="#{uid}" hx-trigger="click[altKey] consume">
            {w}
            </x-w>
            </x-w>
            </x-wc>
        """
    return html

def __note_render(url: str, w: int):
    wx = word_get(w)
    html = f"""<div class="container">
        <form hx-put="{url}" x-w-id={w}>
        <p><textarea placeholder="note" cols="40" rows="6" name="note">{wx[4] if wx[4] else ""}</textarea></p>
        <p><button>Submit</button><button hx-get="{url}">Cancel</button></p>
        </form>
    </div>"""
    return html
