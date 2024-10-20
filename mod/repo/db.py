from mod.util.conf import DB_FILE

import apsw.bestpractice
apsw.bestpractice.apply(apsw.bestpractice.recommended)

class Database:
    con = apsw.Connection(DB_FILE)

    def init(self):
        self.begin()
        self.exec("CREATE TABLE IF NOT EXISTS word(id INTEGER PRIMARY KEY, word TEXT UNIQUE NOT NULL, is_known BOOLEAN NOT NULL, ignore BOOLEAN NOT NULL, note TEXT);")
        self.exec("CREATE TABLE IF NOT EXISTS work(id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL);")
        self.exec("CREATE TABLE IF NOT EXISTS part(id INTEGER PRIMARY KEY, work_id INT NOT NULL, name TEXT NOT NULL, FOREIGN KEY(work_id) REFERENCES work(id));")
        self.exec("CREATE TABLE IF NOT EXISTS part_word(part_id INT NOT NULL, word_id INT NOT NULL, line_no INT NOT NULL, word_no INT NOT NULL, UNIQUE(part_id, line_no, word_no), FOREIGN KEY(part_id) REFERENCES part(id), FOREIGN KEY(word_id) REFERENCES word(id));")
        self.commit()

    def begin(self):
        self.con.execute("BEGIN")

    def exec(self, sql: str, *data):
        return list(self.con.execute(sql, data))

    def commit(self):
        self.con.execute("COMMIT")

    def rollback(self):
        self.con.execute("ROLLBACK")