import {qs, qsa, qs_attr, on_text_content_match, new_el, clear_all_menus} from "./lib.js";

const SVG_FLAG = `<svg class="flag" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><!--!Font Awesome Free 6.7.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2024 Fonticons, Inc.--><path d="M64 32C64 14.3 49.7 0 32 0S0 14.3 0 32L0 64 0 368 0 480c0 17.7 14.3 32 32 32s32-14.3 32-32l0-128 64.3-16.1c41.1-10.3 84.6-5.5 122.5 13.4c44.2 22.1 95.5 24.8 141.7 7.4l34.7-13c12.5-4.7 20.8-16.6 20.8-30l0-247.7c0-23-24.2-38-44.8-27.7l-9.6 4.8c-46.3 23.2-100.8 23.2-147.1 0c-35.1-17.6-75.4-22-113.5-12.5L64 48l0-16z"/></svg>`
const SVG_UNFLAG = `<svg class="flag" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><!--!Font Awesome Free 6.7.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2024 Fonticons, Inc.--><path d="M48 24C48 10.7 37.3 0 24 0S0 10.7 0 24L0 64 0 350.5 0 400l0 88c0 13.3 10.7 24 24 24s24-10.7 24-24l0-100 80.3-20.1c41.1-10.3 84.6-5.5 122.5 13.4c44.2 22.1 95.5 24.8 141.7 7.4l34.7-13c12.5-4.7 20.8-16.6 20.8-30l0-279.7c0-23-24.2-38-44.8-27.7l-9.6 4.8c-46.3 23.2-100.8 23.2-147.1 0c-35.1-17.6-75.4-22-113.5-12.5L48 52l0-28zm0 77.5l96.6-24.2c27-6.7 55.5-3.6 80.4 8.8c54.9 27.4 118.7 29.7 175 6.8l0 241.8-24.4 9.1c-33.7 12.6-71.2 10.7-103.4-5.4c-48.2-24.1-103.3-30.1-155.6-17.1L48 338.5l0-237z"/></svg>`
const SVG_CHECK = `<svg class="mark" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><!--!Font Awesome Free 6.7.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2024 Fonticons, Inc.--><path d="M438.6 105.4c12.5 12.5 12.5 32.8 0 45.3l-256 256c-12.5 12.5-32.8 12.5-45.3 0l-128-128c-12.5-12.5-12.5-32.8 0-45.3s32.8-12.5 45.3 0L160 338.7 393.4 105.4c12.5-12.5 32.8-12.5 45.3 0z"/></svg>`
const SVG_UNCHECK = `<svg class="mark" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512"><!--!Font Awesome Free 6.7.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2024 Fonticons, Inc.--><path d="M342.6 150.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L192 210.7 86.6 105.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3L146.7 256 41.4 361.4c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L192 301.3 297.4 406.6c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3L237.3 256 342.6 150.6z"/></svg>`
const SVG_TAG = `<svg class="tag" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><!--!Font Awesome Free 6.7.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2024 Fonticons, Inc.--><path d="M0 80L0 229.5c0 17 6.7 33.3 18.7 45.3l176 176c25 25 65.5 25 90.5 0L418.7 317.3c25-25 25-65.5 0-90.5l-176-176c-12-12-28.3-18.7-45.3-18.7L48 32C21.5 32 0 53.5 0 80zm112 32a32 32 0 1 1 0 64 32 32 0 1 1 0-64z"/></svg>`

function toggle_word_status(word) {
	on_text_content_match(qsa("w"), word, x => {
		if (x.hasAttribute("is-k")) {
			x.removeAttribute("is-k");
		}
		else {
			x.setAttribute("is-k", "")
		}
	});
}

function toggle_word_flag_status(word) {
	on_text_content_match(qsa("w"), word, x => {
		if (x.hasAttribute("is-f")) {
			x.removeAttribute("is-f");
		}
		else {
			x.setAttribute("is-f", "")
		}
	});
}

function append_before_word(se, name, attrs, html) {
	const x = new_el(name, attrs, html);
	se.before(x);
	htmx.process(x);
}

function prepare_for_word_click(e) {
	if (e.target.localName !== "w") return;
	const se = e.target;
	const word = se.firstChild.textContent.trim();
	const doc_uuid = qs_attr('document', 'uuid');
	se.setAttribute("hx-vals", JSON.stringify({"action": "mark", "word": word, "doc_uuid": doc_uuid}));
	se.setAttribute("hx-post", "/sa/");
	se.setAttribute("hx-swap", "none");
	htmx.process(se);
}

function show_custom_context_menu(e) {
    // prevent the normal context menu from popping up
    e.preventDefault();
    clear_all_menus();

	const se = e.target.closest("w");

	const check = se.hasAttribute("is-k") ? SVG_UNCHECK : SVG_CHECK;
	const flag = se.hasAttribute("is-f") ? SVG_UNFLAG : SVG_FLAG;


	const word = se.firstChild.textContent.trim();
	const doc_uuid = qs_attr('document', 'uuid');

	append_before_word(se, 'nav', {'class': 'context'}, `<ul>
    <li><a hx-swap="none" hx-post="/sa/" hx-vals='${JSON.stringify({"action": "mark", "word": word, "doc_uuid": doc_uuid})}' href="javascript:void(0)">${check}</a></li>
    <li><a hx-swap="none" hx-post="/sa/" hx-vals='${JSON.stringify({"action": "tag", "word": word, "doc_uuid": doc_uuid})}' href="javascript:void(0)">${SVG_TAG}</a></li>
    <li><a hx-swap="none" hx-post="/sa/" hx-vals='${JSON.stringify({"action": "flag", "word": word, "doc_uuid": doc_uuid})}' href="javascript:void(0)">${flag}</a></li>
    </ul>`);

}

function listen_to_word_events() {
	qsa('w').forEach(x => x.addEventListener('contextmenu', show_custom_context_menu));
	qsa('w').forEach(x => x.addEventListener('mousedown', prepare_for_word_click));
}

function handle_htmx() {
	listen_to_word_events();

	document.body.addEventListener('htmx:configRequest', (e) => {
        const te = e.detail.triggeringEvent
		const se = te.target;
		if (te.type === "click") {
			let xid = ""
			const word = e.detail.parameters["word"]
			if (word) {
				switch(e.detail.parameters["action"]) {
					case "mark": {
						toggle_word_status(word);
						break;
					}
					case "tag": {
						const xe = se.closest("nav");
						xid = window.crypto.randomUUID()
						append_before_word(xe, "div", {"id": "id_"+xid, "class": "note-container"}, "")
						e.detail.parameters["xid"] = xid;
						break;
					}
					case "flag": {
						toggle_word_flag_status(word);
						break;
					}
					default: {
						toggle_word_status(word);
					}
				}
			}
			else if (e.detail.parameters["note"] !== undefined) {
				// posting note to server
				e.detail.parameters["hash"] = se.closest("div").getAttribute("hash");
				e.detail.parameters["doc_uuid"] = qs_attr('document', 'uuid');
				qs(".tag-container").remove();
			}
			e.detail.headers["X-CSRFToken"] = qs_attr('document', 'csrftoken');
		}
	});

	document.body.addEventListener('htmx:afterSwap', (e) => {
		if (e.detail.elt.classList.contains("note-container")) {
			const cancel = qs(".cancel")
			if (cancel) {
				cancel.onclick = () => {
					qs(".tag-container").remove();
				};
			}
		}
		else if (e.detail.elt.classList.contains("document-container") && !e.detail.elt.classList.contains("vyakaranam")) {
			listen_to_word_events();
		}
	});
}

export {
    handle_htmx,
};