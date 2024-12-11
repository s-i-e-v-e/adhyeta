function get_default_mode() {
	const m = window.matchMedia(`(prefers-color-scheme: light)`)
	return m.matches ? "light" : "dark";
}

function get_default_font_size() {
	return window.getComputedStyle(document.body).getPropertyValue("--font-size").split("rem")[0]
}

function get_default_font_name() {
	return window.getComputedStyle(document.body).getPropertyValue("--font")
}

function store_config(config) {
	localStorage.setItem("config", JSON.stringify(config));
}

function load_config() {
	let config = JSON.parse(localStorage.getItem("config") || "{}");
	config.scheme = config.scheme || get_default_mode();
	config.theme = config.theme || 0;
	config.font_size = config.font_size || get_default_font_size();
	config.font_name = config.font_name || get_default_font_name();
	return config;
}

export {
	load_config,
	store_config,
}