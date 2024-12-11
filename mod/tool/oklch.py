def generate():
    xs = []
    for h in range(0, 360, 15):
        xs += f"<table><h1>H{h}"
        for c in range(0, 100 + 1, 2):
            xs += f"<tr><td>C{c}</td>"
            for light in range(0, 100+1, 2):
                label = "*" if light in [20, 40, 60, 80] else ""
                xs += f"""<td style="width: 2svw; background: oklch({light}% {c}% {h})">{label}</td>"""
            xs += "</tr>"
        xs += "</table>"
    return "".join(xs)

if __name__ == "__main__":
    with open("a.html", "w") as f:
        f.write(generate())

