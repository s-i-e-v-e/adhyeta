from mod.root.action.vyakaranam.dhatu import build_forms

def classify():
    xs = []
    build_forms(xs)
    for x in xs:
        print(x)
