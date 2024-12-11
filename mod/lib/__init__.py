from typing import Optional


def head(xs: list):
    return xs[0] if len(xs) else None

def fhead(xs: list):
    return xs[0]

def is_empty(xs: list) -> bool:
    return len(xs) == 0

def is_not_empty(xs: list) -> bool:
    return not is_empty(xs)

def list_optional_append[A](self, x: Optional[A]):
    if x is None:
        return
    self.append(x)

def list_head(xs: list):
    return head(xs)

