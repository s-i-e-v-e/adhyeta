# sxml elements that can contain (sanskrit) text
DOC_TEXT_ELEMENTS = ["p", "corr", "title", "\"", "'", "q", "v", "lit", "orig", "tran", "fn"]
# sxml elements that are valid inside a manually created document
VALID_DOC_ELEMENTS = []
VALID_DOC_ELEMENTS.extend(DOC_TEXT_ELEMENTS)
VALID_DOC_ELEMENTS.extend(["chapter", "document", "copyright", "source", "author", "note", "category", "matter", "x-list", "sic", "narration", "dedication", "original", "ref", "song", "poem", "letter", "signature", "toc"])
VALID_DOC_ELEMENTS.extend(["blockquote", "a", "em", "span", "i", "b", "strong", "img", "ul", "ol", "li", "hr", "br", "h1", "article", "section", "header", "footer", "meta"])
VALID_DOC_ELEMENTS.extend(["epigraph", "drama", "scene", "verse", "dedication", "introduction", "cite", "var", "subtitle", "bridgehead", "sq", "dfn", "time", "table", "tbody", "thead", "th", "tr", "td", "persona", "title-notes", "stage-direction", "div", "caption", "tfoot"])
# html-conv: sxml elements that are allowed inside the document
DOC_ELEMENTS = []
DOC_ELEMENTS.extend(["corr", "q", "v", "lit", "orig", "tran", "n", "w", "g", "t"])
DOC_ELEMENTS.extend(["document", "copyright", "author", "note", "category", "matter", "sic", "narration", "dedication", "original", "ref", "song", "poem", "letter", "signature", "toc"])
# html-conv: html elements that are allowed inside the document
DOC_HTML_ELEMENTS = ["p", "blockquote", "a", "em", "i", "img", "ul", "li", "hr", "br", "article", "section", "header", "footer", "div", "span", "form", "input", "button", "h1", "h2", "h3", "link", "ruby", "rt", "audio"]
