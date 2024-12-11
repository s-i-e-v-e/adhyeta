from mod.root.backend.importers.sxml_list import collect_direct_child_dirs

def test_collect_direct_child_dirs():
    parent = '/sa/k/l/kalidasa'
    xs = [
        '/sa/k/l/kalidasa/rtusamharam/index.sxml',
        '/sa/k/l/kalidasa/meghasandesam.sxml',
        '/sa/k/l/kalidasa/sakuntalam/index.sxml',
    ]
    ys = collect_direct_child_dirs(parent, xs)
    assert ys == [
        '/sa/k/l/kalidasa/rtusamharam/index.sxml',
        '/sa/k/l/kalidasa/sakuntalam/index.sxml',
    ]