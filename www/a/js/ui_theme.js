import { load_config, store_config } from "./config.js";
import {clear_all_menus, new_el, qs, qsa} from "./lib.js";

const UNI_THEMES = ["0", "015", "030", "045", "060", "075", "090", "105", "120", "135", "150", "165", "180", "195", "210", "225", "240", "255", "270", "285", "300", "315", "330", "345", ].map(x => "theme-uni-"+x);
const THEMES= []
THEMES.push(...UNI_THEMES);

function theme_update() {
	const config = load_config();
	const n = config.theme !== undefined ? config.theme : 0;// ((config.theme + 1) % THEMES.length) : config.theme;

	const UNI = "theme-uni"
	const e = document.body.parentElement
	e.classList.remove(UNI);
	for (let x of THEMES) {
		e.classList.remove(x);
	}
	const theme = THEMES[n]
	e.classList.add(theme);
	if (theme.startsWith(UNI)) {
		e.classList.add(UNI);
	}

	config.theme = n
	store_config(config);
}

function theme_set(n) {
	const config = load_config();
	config.theme = n
	store_config(config);
}

function theme_show_menu() {
	const config = load_config();
	const n = config.theme !== undefined ? config.theme : 0;
	let html = ""
	let i = 0
	for (let t of THEMES) {
		const star = n === i ? "*" : " "
		html += `
<div class="theme-uni ${t}" style="padding:0.25em; cursor: pointer">
<span style="padding:0.25em; border-bottom: 1px dotted grey; color: var(--color-text); background-color: var(--color-back)">${star}ॐ</span>
<span style="padding:0.25em; border-bottom: 1px dotted grey; color: var(--color-text-alt); background-color: var(--color-back-alt)">रामो</span>
<span style="padding:0.25em; border-bottom: 1px dotted grey; color: var(--color-text-em); background-color: var(--color-back)">राजमणिः</span>
<span style="padding:0.25em; border-bottom: 1px dotted grey; color: var(--color-text-em-alt); background-color: var(--color-back-alt)">सदा</span>
<span style="padding:0.25em; border-bottom: 1px dotted grey; color: var(--color-text); background-color: var(--color-back-alt)">विजयते</span>
<span style="padding:0.25em; border-bottom: 1px dotted grey; color: var(--color-text-alt); background-color: var(--color-back)">रामं</span>
<span style="padding:0.25em; border-bottom: 1px dotted grey; color: var(--color-text-em); background-color: var(--color-back-alt)">रमेशं</span>
<span style="padding:0.25em; border-bottom: 1px dotted grey; color: var(--color-text-em-alt); background-color: var(--color-back)">भजे</span>
<span style="padding:0.25em; border-bottom: 1px dotted grey; color: var(--color-sep); background-color: var(--color-back);">---</span>
<span style="padding:0.25em; border-bottom: 1px dotted grey; color: var(--color-meta); background-color: var(--color-back);">meta</span>
</div>`.replace("\n", "").replaceAll("\n", "")
		i += 1
	}

    const x = new_el("div", {"class": "context"}, `
<div style="padding: 0; margin: 0; line-height: 1">
    ${html}
</div>
    `);
    clear_all_menus();
    qs("#ephemeral").appendChild(x);
	qsa("#ephemeral .theme-uni").forEach(x => x.addEventListener("click", e => {
		e.stopPropagation();
		const n = THEMES.indexOf(e.target.closest("div").classList.item(1));
        theme_set(n);
		theme_update();
    }));
}

export {
	theme_update,
	theme_show_menu,
};