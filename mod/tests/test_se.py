from mod.root.backend.importers.tp.se_download import SeSource, parse_book

ivfs = dict()
ovfs = dict()

base = ''
base_out = ''

def set_expected_index_content(f: str, body: str, work: str, book_title: str, book_author: str):
    author, title = work.split('_')
    cbody = f'<toc>\n{body}\n</toc>' if body else '<toc\n/>'
    ovfs[base + '/' + f] = f'''
<document uuid="">
<meta>
<copyright>CC0/PD. No rights reserved</copyright>
<source url="https://standardebooks.org/ebooks/{author}/{title}">Standard Ebooks</source>
<title>{book_title}</title>
<author>{book_author}</author>
</meta>
{cbody}
</document>
            '''.strip()

def set_expected_content(f: str, meta: str, body: str, work: str):
    author, title = work.split('_')
    cbody = f'<chapter>\n{body}\n</chapter>' if body else '<chapter/>'
    ovfs[base + '/' + f] = f'''
<document uuid="">
<meta>
<copyright>CC0/PD. No rights reserved</copyright>
<source url="https://standardebooks.org/ebooks/{author}/{title}">Standard Ebooks</source>
{meta}
</meta>
{cbody}
</document>
            '''.strip()
def set_content(f: str, x: str):
    ivfs[base+'/'+f] = f'''
    <?xml version="1.0" encoding="utf-8"?>
        <html>
        <body>{x.strip()}</body>
        </html>
        '''.strip()

def set_opf(title: str, author: str):
    set_content('content.opf', f'''
    <data>
        <dc:title id="title">{title}</dc:title>
        <dc:title id="subtitle"></dc:title>
        <dc:title id="fulltitle"></dc:title>
        <meta property="se:word-count">50000</meta>
        <dc:creator id="author">{author}</dc:creator>
    </data>
    ''')
def write_text(f: str, x: str):
    print('writing ' + f)
    assert ovfs[f] == x

def read_text(f: str):
    return ivfs[f]

def exists(f: str):
    return f in ivfs

def test_eap():
    # notes in title
    pass

def get_ses(work: str):
    return SeSource(base, base_out, work, read_text, write_text, exists)

def test_th_tess_of_the_durbervilles():
    work = 'thomas-hardy_tess-of-the-durbervilles'
    book_title = 'Tess of the d’Urbervilles'
    book_author = 'Thomas Hardy'
    set_opf(book_title, book_author)

    toc = '''
            <nav><ol>
            <li>
                <a href="text/halftitlepage.xhtml">Tess of the d’Urbervilles</a>
                <ol>
                    <li>
                        <a href="text/part-1.xhtml">Phase the First: The Maiden</a>
                        <ol>
                            <li>
                                <a href="text/chapter-1.xhtml" epub:type="z3998:roman">I</a>
                            </li>
                        </ol>
                    </li>
                    <li>
                        <a href="text/part-2.xhtml">Phase the Second: Maiden No More</a>
                        <ol>
                            <li>
                                <a href="text/chapter-12.xhtml" epub:type="z3998:roman">XII</a>
                            </li>
                        </ol>
                    </li>
                </ol>
            </li>
            </ol></nav>
            '''

    half_title = '''
    		<section id="halftitlepage" epub:type="halftitlepage">
    			<hgroup epub:type="fulltitle">
    				<h2 epub:type="title">Tess of the d’Urbervilles</h2>
    				<p epub:type="subtitle">A Pure Woman Faithfully Presented</p>
    			</hgroup>
    		</section>
    '''
    part_1 = '''
    				<section id="part-1" epub:type="part">
			<hgroup>
				<h2>
					<span epub:type="label">Phase</span>
					<span epub:type="ordinal">the First</span>
				</h2>
				<p epub:type="title">The Maiden</p>
			</hgroup>
		</section>
                '''
    part_2 = '''
            		<section id="part-2" epub:type="part">
			<hgroup>
				<h2>
					<span epub:type="label">Phase</span>
					<span epub:type="ordinal">the Second</span>
				</h2>
				<p epub:type="title">Maiden No More</p>
			</hgroup>
		</section>
                '''

    ch_1 = '''
        				<section data-parent="part-1" id="chapter-1" epub:type="chapter">
			<h3 epub:type="ordinal z3998:roman">I</h3>
			<p>“Good night t’ee,” said the man with the basket.</p>
    			</section>
        '''
    ch_12 = '''		<section data-parent="part-2" id="chapter-12" epub:type="chapter">
			<h3 epub:type="ordinal z3998:roman">XII</h3>
			<p>The basket was heavy and the bundle was large,</p></section>'''

    set_content('toc.xhtml', toc)
    set_content('text/halftitlepage.xhtml', half_title)
    set_content('text/part-1.xhtml', part_1)
    set_content('text/part-2.xhtml', part_2)
    set_content('text/chapter-1.xhtml', ch_1)
    set_content('text/chapter-12.xhtml', ch_12)

    set_expected_content('tess-of-the-durbervilles.xml', '<title>Tess of the d’Urbervilles</title>\n<subtitle>A Pure Woman Faithfully Presented</subtitle>', '', work)
    set_expected_content('the-maiden.xml', '<title label="Phase" n="the First">The Maiden</title>', '', work)
    set_expected_content('maiden-no-more.xml', '<title label="Phase" n="the Second">Maiden No More</title>', '', work)
    set_expected_content('i.xml', '<title n="I"/>', '<p>“Good night t’ee,” said the man with the basket.</p>', work)
    set_expected_content('xii.xml', '<title n="XII"/>', '<p>The basket was heavy and the bundle was large,</p>', work)

    INDEX = '''
<ref url="the-maiden.xml" label="Phase" n="the First">The Maiden</ref>
<ref url="i.xml" n="I"/>
<ref url="maiden-no-more.xml" label="Phase" n="the Second">Maiden No More</ref>
<ref url="xii.xml" n="XII"/>
'''.strip()

    set_expected_index_content('index.xml', INDEX, work, book_title, book_author)
    ses = get_ses(work)
    parse_book(ses)

def test_ew_house_of_mirth():
    work = 'edith-wharton_the-house-of-mirth'
    book_title = 'The House of Mirth'
    book_author = 'Edith Wharton'
    set_opf(book_title, book_author)

    toc ='''
            <nav><ol>
            <li><a href="text/book-1.xhtml">Book <span epub:type="z3998:roman">I</span></a><ol>
                <li><a href="text/chapter-1-1.xhtml" epub:type="z3998:roman">I</a></li>
            </ol></li>
            <li><a href="text/book-2.xhtml">Book <span epub:type="z3998:roman">II</span></a><ol>
                <li><a href="text/chapter-2-1.xhtml" epub:type="z3998:roman">I</a></li>
            </ol></li>
            </ol></nav>
            '''

    book_1 = '''
            <section id="book-1" epub:type="part">
                <h2>
                    <span epub:type="label">Book</span>
                    <span epub:type="ordinal z3998:roman">I</span>
                </h2>
            </section>
                '''
    book_2  = '''
            <section id="book-2" epub:type="part">
                <h2>
                    <span epub:type="label">Book</span>
                    <span epub:type="ordinal z3998:roman">II</span>
                </h2>
            </section>
                '''
    ch_1_1 = '''
                <section data-parent="book-1" id="chapter-1-1" epub:type="chapter">
                <h3 epub:type="ordinal z3998:roman">I</h3>
                <p>Selden paused in surprise.</p>
                </section>
        '''
    ch_2_1 = '''		<section data-parent="book-2" id="chapter-2-1" epub:type="chapter">
                <h3 epub:type="ordinal z3998:roman">I</h3>
                <p>It came vividly to Selden on the Casino steps that Monte Carlo had</p></section>
        '''

    set_content('toc.xhtml', toc)
    set_content('text/book-1.xhtml', book_1)
    set_content('text/book-2.xhtml', book_2)
    set_content('text/chapter-1-1.xhtml', ch_1_1)
    set_content('text/chapter-2-1.xhtml', ch_2_1)

    set_expected_content('book-i.xml', '<title label="Book" n="I"/>', '', work)
    set_expected_content('book-ii.xml', '<title label="Book" n="II"/>', '', work)
    set_expected_content('i-i.xml', '<title n="I"/>','<p>Selden paused in surprise.</p>', work)
    set_expected_content('ii-i.xml', '<title n="I"/>', '<p>It came vividly to Selden on the Casino steps that Monte Carlo had</p>', work)
    INDEX = '''
<ref url="book-i.xml" label="Book" n="I"/>
<ref url="i-i.xml" n="I"/>
<ref url="book-ii.xml" label="Book" n="II"/>
<ref url="ii-i.xml" n="I"/>
'''.strip()
    set_expected_index_content('index.xml', INDEX, work, book_title, book_author)

    ses = get_ses(work)
    parse_book(ses)

def test_black_beauty():
    work = 'anna-sewell_black-beauty'
    book_title = 'Black Beauty'
    book_author = 'Anna Sewell'
    set_opf(book_title, book_author)
    toc = '''
        <nav><ol>
        <li><a href="text/titlepage.xhtml">Titlepage</a></li>
        <li><a href="text/part-1.xhtml">Part <span epub:type="z3998:roman">I</span></a>
        <ol>
        <li><a href="text/chapter-1.xhtml"><span epub:type="z3998:roman">I</span>: My Early Home</a></li>
        </ol></li>
        </ol></nav>
        '''
    part_1 = '''
		<section id="part-1" epub:type="part">
			<h2>
				<span epub:type="label">Part</span>
				<span epub:type="ordinal z3998:roman">I</span>
			</h2>
		</section>
            '''

    ch_1 = '''
    		<section data-parent="part-1" id="chapter-1" epub:type="chapter">
			<hgroup>
				<h3 epub:type="ordinal z3998:roman">I</h3>
				<p epub:type="title" xml:lang="en">My Early Home</p>
			</hgroup>
			<p>The first place that I can well remember was a large pleasant meadow with a pond of clear water in it. <span epub:type="z3998:roman">X</span></p>
			</section>
    '''
    set_content('toc.xhtml', toc)
    set_content('text/part-1.xhtml', part_1)
    set_content('text/chapter-1.xhtml', ch_1)

    set_expected_content('part-i.xml', '<title label="Part" n="I"/>', '', work)
    set_expected_content('my-early-home.xml', '<title lang="en" n="I">My Early Home</title>', '<p>The first place that I can well remember was a large pleasant meadow with a pond of clear water in it. <span>X</span></p>', work)
    INDEX = '''
<ref url="part-i.xml" label="Part" n="I"/>
<ref url="my-early-home.xml" n="I">My Early Home</ref>
'''.strip()
    set_expected_index_content('index.xml', INDEX, work, book_title, book_author)

    ses = get_ses(work)
    parse_book(ses)