import sys
import mod.tool.ocr as ocr
import mod.tool.www.publish as pub
import mod.tool.www.publish_html as pub_html

if __name__ == '__main__':
    if sys.argv[1] == "ocr":
        dir_in = sys.argv[2]
        base = sys.argv[3]
        ocr.run(dir_in, base)
    elif sys.argv[1] == "publish":
        force = sys.argv[2] == "--force" if len(sys.argv) > 2 else False
        pub.run(force)
    elif sys.argv[1] == "publish-app":
        pub_html.run()
    else:
        pass
