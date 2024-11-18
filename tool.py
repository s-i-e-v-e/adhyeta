import sys

import mod.tools.adhyeta_www as www
import mod.tools.adhyeta_consolidate as cons
import mod.tools.ocr as ocr
if __name__ == '__main__':
    if sys.argv[1] == "publish":
        dir_in = sys.argv[2]
        dir_out = sys.argv[3]
        www.run(dir_in, dir_out)
    elif sys.argv[1] == "consolidate":
        dir_in = sys.argv[2]
        dir_out = sys.argv[3]
        cons.run(dir_in, dir_out)
    elif sys.argv[1] == "ocr":
        dir_in = sys.argv[2]
        base = sys.argv[3]
        ocr.run(dir_in, base)
    else:
        pass
