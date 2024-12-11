from dataclasses import dataclass
from mod.lib.sqlite_db import Database, Row
from typing import Type

def __fbuild[A](a: Type[A], xs: Row|None) -> A:
    assert xs is not None
    return a(*xs)

def __build[A](a: Type[A], xs: Row|None) -> A|None:
    return a(*xs) if xs else None

def __list[A](a: Type[A], xss: list[Row]) -> list[A]:
    return [x for x in [__build(a, xs) for xs in xss] if x is not None]
