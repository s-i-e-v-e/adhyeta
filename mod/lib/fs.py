import os
from dataclasses import dataclass
import shutil
from pathlib import Path
from os import listdir
from os.path import isfile, isdir, join
import json

@dataclass
class File:
    name: str
    parent: str
    full_path: str

def abs(path: str) -> str:
    return Path(path).absolute().__str__()

def to_file(path: str):
    xs = path.split("/")
    return File(xs[-1], '/'.join(xs[:-1]), path)

def stat(path: str):
    return os.stat(Path(path))

def list_files(path: str):
    xs = [f for f in listdir(path) if isfile(join(path, f))]
    xs.sort()
    return [File(x, path, join(path, x)) for x in xs]

def list_dirs(path: str):
    xs = [f for f in listdir(path) if isdir(join(path, f))]
    xs.sort()
    return [File(x, path, join(path, x)) for x in xs]

def rm(path: str):
    if exists(path):
        os.remove(path)

def exists(path: str):
    p = Path(path)
    return p.exists()

def read_text(path: str):
    with open(path, 'r') as f:
        return f.read()

def write_text(path: str, data: str):
    ensure_parent(path)
    with open(path, 'w') as f:
        return f.write(data)

def append_text(path: str, data: str):
    ensure_parent(path)
    with open(path, 'a') as f:
        return f.write(data)

def read_json(path: str):
    return json.loads(read_text(path))

def get_parent(path: str):
    return Path(path).parent.__str__()

def ensure_parent(path: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)

def copy_file(src: str, dst: str):
    ensure_parent(dst)
    shutil.copyfile(src, dst)

def copy_tree(src: str, dst: str):
    ensure_parent(dst)
    shutil.copytree(src, dst, dirs_exist_ok=True)

def exec(cmd: list[str], cwd: str):
    import subprocess
    result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
    return result.stdout.decode('utf-8').splitlines()
