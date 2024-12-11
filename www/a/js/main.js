import { theming_init } from "./theming.js";
import { handle_htmx } from "./events.js";
import {clear_all_menus} from "./lib";


function init() {
	document.body.addEventListener('click', e => {
		clear_all_menus()
	});
	theming_init();
	if (!document.body.classList.contains("app")) return;
	handle_htmx();
}

window.addEventListener('DOMContentLoaded', init);
