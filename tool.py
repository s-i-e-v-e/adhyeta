import sys
import mod.tool.ocr as ocr
import mod.tool.uuid as uuid

if __name__ == '__main__':
    if sys.argv[1] == "ocr":
        dir_in = sys.argv[2]
        base = sys.argv[3]
        ocr.run(dir_in, base)
    elif sys.argv[1] == "uuid":
        uuid.run()
    else:
        pass
