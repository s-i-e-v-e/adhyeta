function qs(x) {
	return document.querySelector(x);
}

function qs_attr(x, a) {
	return qs(x).getAttribute(a);
}

function qsa(x) {
	return document.querySelectorAll(x);
}

function on_text_content_match(xs, text, fn) {
	for (let x of xs) {
		if (x.textContent !== text) continue;
		fn(x);
	}
}

function new_el(name, attrs, html) {
	const x = document.createElement(name);
	for (let k in attrs) {
		x.setAttribute(k, attrs[k]);
	}
	x.innerHTML = html;
	return x;
}

function clear_all_menus() {
	qsa("nav[class=context]").forEach(x => x.remove());
	qs("#ephemeral").innerHTML = "";
}

export {
    qs,
    qsa,
    qs_attr,
	new_el,
    on_text_content_match,
	clear_all_menus,
};