import apsw

import apsw.bestpractice
apsw.bestpractice.apply(apsw.bestpractice.recommended)

class Database:
    con = apsw.Connection(":memory:")

    def init(self):
        self.begin()
        self.exec("CREATE TABLE IF NOT EXISTS book(id INTEGER PRIMARY KEY, loc TEXT UNIQUE NOT NULL, title TEXT, content BLOB);")
        self.commit()

    def begin(self):
        self.con.execute("BEGIN")

    def exec(self, sql: str, *data):
        return list(self.con.execute(sql, data))

    def commit(self):
        self.con.execute("COMMIT")

    def rollback(self):
        self.con.execute("ROLLBACK")
