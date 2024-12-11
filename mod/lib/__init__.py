def head(xs: list):
    return xs[0] if len(xs) else None

def is_empty(xs: list) -> bool:
    return len(xs) == 0

def is_not_empty(xs: list) -> bool:
    return not is_empty(xs)