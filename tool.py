import sys

import mod.tools.www.publish as pub
import mod.tools.ocr as ocr
if __name__ == '__main__':
    if sys.argv[1] == "publish":
        dir_in = sys.argv[2]
        dir_out = sys.argv[3]
        pub.run(dir_in, dir_out)
    elif sys.argv[1] == "ocr":
        dir_in = sys.argv[2]
        base = sys.argv[3]
        ocr.run(dir_in, base)
    else:
        pass
