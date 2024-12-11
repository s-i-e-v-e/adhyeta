import os
import argon2
import scrypt
from argon2 import PasswordHasher, Parameters, Type
ph = PasswordHasher.from_parameters(Parameters(Type.ID, 19, 16, 16, 1, 256*1024, 1))

def hash_password_argon2id(password: str) -> str:
    return ph.hash(password)

def verify_password_argon2id(hash: str, password: str) -> tuple[bool, str]:
    try:
        ph.verify(hash, password)
        if ph.check_needs_rehash(hash):
            hash = hash_password_argon2id(password)
            return True, hash
        else:
            return True, ""
    except argon2.exceptions.VerifyMismatchError:
        return False, ""

def hash_password_scrypt(password: str, maxtime=0.5, datalength=64) -> bytes:
    return scrypt.encrypt(os.urandom(datalength), password, maxtime=maxtime)

def verify_password_scrypt(hashed_password: bytes, guessed_password: str, maxtime=0.5):
    try:
        scrypt.decrypt(hashed_password, guessed_password, maxtime)
        return True
    except scrypt.error:
        return False
