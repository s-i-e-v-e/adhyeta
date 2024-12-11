from mod.lib import uuid

def run(count: int):
    for i in range(0, count):
        print(uuid.gen())
