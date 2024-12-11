const SCHEME_BUTTON = ".icon";
const HTML = "html";

function qs(x) {
	return document.querySelector(x);
}

function set_session_property(k, v) {
	localStorage.setItem(k, v);
}

function get_session_property(k) {
	return localStorage.getItem(k);
}

function switch_mode(mode) {
	const vb = {
		"light": "0 0 384 512",
		"dark": "0 0 512 512",
	}
	const d = {
		"light": "M223.5 32C100 32 0 132.3 0 256S100 480 223.5 480c60.6 0 115.5-24.2 155.8-63.4c5-4.9 6.3-12.5 3.1-18.7s-10.1-9.7-17-8.5c-9.8 1.7-19.8 2.6-30.1 2.6c-96.9 0-175.5-78.8-175.5-176c0-65.8 36-123.1 89.3-153.3c6.1-3.5 9.2-10.5 7.7-17.3s-7.3-11.9-14.3-12.5c-6.3-.5-12.6-.8-19-.8z",
		"dark": "M361.5 1.2c5 2.1 8.6 6.6 9.6 11.9L391 121l107.9 19.8c5.3 1 9.8 4.6 11.9 9.6s1.5 10.7-1.6 15.2L446.9 256l62.3 90.3c3.1 4.5 3.7 10.2 1.6 15.2s-6.6 8.6-11.9 9.6L391 391 371.1 498.9c-1 5.3-4.6 9.8-9.6 11.9s-10.7 1.5-15.2-1.6L256 446.9l-90.3 62.3c-4.5 3.1-10.2 3.7-15.2 1.6s-8.6-6.6-9.6-11.9L121 391 13.1 371.1c-5.3-1-9.8-4.6-11.9-9.6s-1.5-10.7 1.6-15.2L65.1 256 2.8 165.7c-3.1-4.5-3.7-10.2-1.6-15.2s6.6-8.6 11.9-9.6L121 121 140.9 13.1c1-5.3 4.6-9.8 9.6-11.9s10.7-1.5 15.2 1.6L256 65.1 346.3 2.8c4.5-3.1 10.2-3.7 15.2-1.6zM160 256a96 96 0 1 1 192 0 96 96 0 1 1 -192 0zm224 0a128 128 0 1 0 -256 0 128 128 0 1 0 256 0z",
	};

	const html = qs(HTML);
	html.style.setProperty("color-scheme", mode);

	const x = qs(SCHEME_BUTTON);
	x.setAttribute("viewBox", vb[mode]);
	x.children[0].setAttribute("d", d[mode]);
	set_session_property("mode", mode);
}

function toggle_mode() {
	const mode = get_session_property("mode")
	switch_mode(mode === "light" ? "dark" : "light");
}

function get_mode(mode) {;
	return window.matchMedia(`(prefers-color-scheme: ${mode})`)
}

function hook_mode_switch(mode) {
	const x = get_mode(mode);
	x.addEventListener("change", e => e.matches && switch_mode(mode));
}

function init() {
	const x = qs(SCHEME_BUTTON).parentElement;
	x.addEventListener("click", (e) => {
		toggle_mode();
		return true;
	});
	x.addEventListener("keydown", (e) => {
		if (e.key === "Enter") {
			e.preventDefault();
			toggle_mode();
		}
		return true;
	});


	let m = get_session_property("mode");
	m = m || (get_mode("light").matches ? "light" : "dark");
	switch_mode(m);

	// handle menu
	const a = qs("#account")
	if (a) {
		a.addEventListener("click", (e) => {
			if (!e.target.textContent.includes("{{USER}}")) {
				const nav = qs("#main-nav") || document.createElement("nav");

				if (!nav.id) {
					nav.id = "main-nav";
					nav.classList.add("hide");
					nav.innerHTML = `<li><a href="/logout">logout</a></li>`;
					qs("main").prepend(nav);
				}

				if (nav.classList.contains("hide")) {
					nav.classList.remove("hide");
				}
				else {
					nav.classList.add("hide");
				}
			}
		})
	}

}

window.onload = (e) => init();
