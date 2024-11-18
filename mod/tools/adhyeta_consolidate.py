from shutil import Error
import typing
from mod.util.fs import list_dirs, list_files, read_text, copy_file
from mod.util.sxml import SxmlNode, sxml_parse


def consolidate(sd: str, dd: str):
    for f in list_dirs(sd):
        consolidate(f"{sd}/{f}", dd)

    for f in list_files(sd):
        sf = f"{sd}/{f}"
        if not f.endswith(".sxml"):
            raise Error(f"Expected an SXML file. Found {f}")
        else:
            data = read_text(sf)
            n = sxml_parse(data)
            n = typing.cast(SxmlNode, n)
            uri = n.attrs["uri"]
            df = f"{dd}{uri}.sxml"
            print(f"> {sf} => {df}")
            copy_file(sf, df)

def run(sd: str, dd: str):
    consolidate(sd, dd)