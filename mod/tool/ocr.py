import os
import subprocess

from mod.lib.fs import list_files

def run(sd: str, base: str):
    for sf in list_files(sd):
        xs = sf.name.split('.')
        if xs[-1] not in ["png", "jpg", "jpeg", "ppm", "pbm", "webp"]:
            continue
        xs.pop()

        df = os.path.join(sd, base+"".join(xs))
        subprocess.run(["tesseract", sf.full_path, df, "-l", "san"])