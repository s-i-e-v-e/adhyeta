class ParserState:
    i: int
    max: int
    xx: str

    def __init__(self, xx: str):
        self.xx = xx
        self.i = 0
        self.max = len(xx)

    def error(self, m: str, idx: int):
        idx = idx if idx else self.i
        line = 1 + self.xx.count('\n', 0, idx)
        a = self.xx.rfind('\n', 0, idx)
        b = self.xx.find('\n', idx)
        char = idx - a
        x = self.xx[idx:b]
        return Exception(f"{m}: {x} (L{line}C{char})")

    def eos(self):
        return self.i >= self.max

    def peek(self):
        if self.eos():
            return ''
        return self.xx[self.i]

    def next(self):
        if self.eos():
            return ''
        x = self.xx[self.i]
        self.i += 1
        return x