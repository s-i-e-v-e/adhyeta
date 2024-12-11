import {load_config, store_config} from "./config.js";
import {qs} from "./lib.js";

function set_mode(mode) {
	const html = qs("html");
	html.style.setProperty("color-scheme", mode);
	const config = load_config();
	config.scheme = mode
	store_config(config);
}

function toggle_mode() {
	const mode = load_config().scheme;
	set_mode(mode === "light" ? "dark" : "light");
}

export {
	set_mode,
	toggle_mode
}