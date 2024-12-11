import apsw
import apsw.bestpractice
apsw.bestpractice.apply(apsw.bestpractice.recommended)

class Database:
    con: apsw.Connection

    def __init__(self, file: str, sql: list[str]):
        self.con = apsw.Connection(file)
        self.begin()
        for s in sql:
            self.exec(s)
        self.commit()

    def begin(self):
        self.con.execute("BEGIN")

    def exec(self, sql: str, *data):
        return list(self.con.execute(sql, data))

    def commit(self):
        self.con.execute("COMMIT")

    def rollback(self):
        self.con.execute("ROLLBACK")
