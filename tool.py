import sys
import mod.tool.ocr as ocr

if __name__ == '__main__':
    if sys.argv[1] == "ocr":
        dir_in = sys.argv[2]
        base = sys.argv[3]
        ocr.run(dir_in, base)
    else:
        pass
