from mod.lib.sqlite_db import Database
from mod.root.action.pub import VirtualFS
from mod.root.data import doc

def build_vfs(db: Database) -> VirtualFS:
    q = VirtualFS()

    def add_to_parent(loc: str):
        def add(p: str, c: str):
            if p != c:
                q[p].append(c)

        xs = loc.split("/")
        ys = []
        pp = ""
        for x in xs:
            ys.append(x)
            yy = "/".join(ys)
            if yy not in q:
                q[yy] = []
            add(pp, yy)
            pp = yy

        ys = xs[0:-1]
        yy = "/".join(ys)
        add(yy, loc)

    for d in doc.list(db):
        add_to_parent(d.loc)

    for k in q.keys():
        xs = list(set(q[k]))

        for f in xs:
            if f.endswith("/index.sxml"):
                xs.remove(f)
                xs.insert(0, f)
                break
        q[k] = xs
    return q