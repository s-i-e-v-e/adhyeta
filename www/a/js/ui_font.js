import {clear_all_menus, new_el, qs} from "./lib.js";
import {load_config, store_config} from "./config.js";

function font_set_size(c) {
    qs("html").style.setProperty("--font-size", `${c.font_size}rem`);
}

function font_set_name(c) {
    const xs = fonts.filter(x => x.name === c.font_name);
    const f = xs.length ? xs[0] : fonts[3];
    c.font_name = f.name;

    qs("html").style.setProperty("--font", `'${c.font_name}'`);
    const s = document.createElement("link");
    s.setAttribute("rel", "stylesheet");
    s.setAttribute("href", f.url);
    document.head.appendChild(s)
}

function font_update() {
    const c = load_config();
    font_set_size(c);
    font_set_name(c);
    store_config(c);
}

const fonts = [
    {url: "/a/font/annapurna.css", name: "Annapurna SIL"},
    {url: "/a/font/kalam.css", name: "Kalam"},
    {url: "/a/font/mukta.css", name: "Mukta"},
    {url: "/a/font/notosans.css", name: "Noto Sans Devanagari"},
    {url: "/a/font/shobhika.css", name: "Shobhika"},
    {url: "/a/font/siddhanta.css", name: "Siddhanta"},
];

function font_show_menu() {
    const c = load_config();
    let font_html = "";
    for (let f of fonts) {
        const selected = f.name === c.font_name ? " selected" : "";
        font_html += `<option${selected} value="${f.url}">${f.name}</option>`
    }

    const x = new_el("div", {"class": "context"}, `
<div>
    <input type="range" list="markers" min="0.5" max="4" step="0.25" value="${c.font_size}" />
    <datalist id="markers">
      <option value="0.50" label="&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"></option>
      <option value="0.75"></option>
      <option value="1.00" label="1&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"></option>
      <option value="1.25"></option>
      <option value="1.50"></option>
      <option value="1.75"></option>
      <option value="2.00" label="2&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"></option>
      <option value="2.25"></option>
      <option value="2.50"></option>
      <option value="2.75"></option>
      <option value="3.00" label="3&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"></option>
      <option value="3.25"></option>
      <option value="3.50"></option>
      <option value="3.75"></option>
      <option value="4.00" label="4"></option>
    </datalist>
    <select id="select-font">${font_html}</select>
</div>
    `);
    clear_all_menus();
    qs("#ephemeral").appendChild(x);

    qs("#ephemeral").addEventListener("click", e => {
        e.stopPropagation();
    });
    qs("#ephemeral input").addEventListener("change", e => {
        const c = load_config();
        c.font_size = e.target.value;
        font_set_size(c);
        store_config(c)
    });

    qs("#select-font").addEventListener("change", async e => {
        const c = load_config();
        c.font_name = e.target.options[e.target.selectedIndex].textContent;

        // const font = new FontFace(c.font_name, `url('${url}')`);
        // document.fonts.add(font)
        // await font.load()

        font_set_name(c);
        store_config(c)
    });
}

export {
    font_update,
    font_show_menu,
}