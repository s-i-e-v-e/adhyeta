from os import listdir
from os.path import isfile, isdir, join
import json

def list_files(path: str):
    xs = [f for f in listdir(path) if isfile(join(path, f))]
    xs.sort()
    return xs

def list_dirs(path: str):
    xs = [f for f in listdir(path) if isdir(join(path, f))]
    xs.sort()
    return xs

def read_text(path: str):
    with open(path, 'r') as f:
        return f.read()

def read_json(path: str):
    return json.loads(read_text(path))
