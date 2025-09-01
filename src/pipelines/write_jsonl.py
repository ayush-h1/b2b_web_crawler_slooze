from __future__ import annotations
import orjson, os
class JsonlWriter:
    def __init__(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.f = open(path, "wb")
    def write_one(self, obj):
        self.f.write(orjson.dumps(obj) + b"\n")
    def close(self):
        if self.f: self.f.close()
