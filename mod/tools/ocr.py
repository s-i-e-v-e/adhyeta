import os
import subprocess

from mod.util.fs import list_files

def run(sd: str, base: str):
    for f in list_files(sd):
        fn, ext = f.split('.')
        if ext not in ["png", "jpg", "jpeg", "ppm", "pbm"]:
            continue

        sf = os.path.join(sd, f)
        df = os.path.join(sd, base+fn)
        subprocess.run(["tesseract", sf, df, "-l", "san"])