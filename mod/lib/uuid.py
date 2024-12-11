import typing

from uuid_extensions import uuid7
chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

def gen():
    n = typing.cast(int, uuid7(as_type="int"))
    arr = []
    base = len(chars)
    while n:
        n, rem = divmod(n, base)
        arr.append(chars[rem])
    arr.reverse()
    return ''.join(arr)