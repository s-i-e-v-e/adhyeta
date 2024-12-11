from apsw import bestpractice, Connection
bestpractice.apply(bestpractice.recommended)

from typing import Any
Row = tuple[Any, ...]

class Database:
    con: Connection

    def __init__(self, file: str, sql: list[str]):
        self.con = Connection(file)
        self.begin()
        for s in sql:
            self.exec(s)
        self.commit()

    def begin(self):
        self.con.execute("BEGIN")

    def exec(self, sql: str, *data) -> list[Row]:
        return list(self.con.execute(sql, data))

    def head(self, sql: str, *data) -> Row|None:
        xs = self.exec(sql, *data)
        return xs[0] if xs else None

    def fhead(self, sql: str, *data) -> Row:
        x = self.head(sql, *data)
        assert x is not None
        return x

    def commit(self):
        self.con.execute("COMMIT")

    def rollback(self):
        self.con.execute("ROLLBACK")
