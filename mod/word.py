from mod.repo.works import word_filter

def word_list_page_render(word_id: int):
    n = 25
    xs = word_filter(word_id, n)
    prev = f"""<a href="/e/word/{word_id - n}">Prev</a>""" if word_id > n else "Prev"
    next = f"""<a href="/e/word/{word_id + n}">Next</a>""" if len(xs) == n else "Next"
    html = ""
    html += """<div hx-push-url="true">"""
    html += f"""<p>{prev} | {next}</p>"""""
    html += """<table>"""
    html += """<tr>
    <th>Word</th>
    <th>Note</th>
    </tr>
    """
    for [id, word, is_known, note] in xs:
        html += f"""<tr>
            <td>{word}</td>
            <td>{note if note else ""}</td>
            </tr>
            """
    html += """</table>"""
    html += """</div>"""
    return html