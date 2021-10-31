import hashlib
import collections

class Hash:
    def __init__(self, data = None):
        self.crypt = hashlib.sha256()
        self.encoding = 'utf-8'
        if data:
            self.write(data)

    def write(self, data):
        self.crypt.update(str(data).encode('utf-8'))

    def compute(self):
        return self.crypt.digest()

def obj_canonical(obj):
    if isinstance(obj, dict):
        return [[obj_canonical(k), obj_canonical(obj[k])] for k in sorted(obj.keys())]
    elif isinstance(obj, list):
        return [obj_canonical(i) for i in obj]
    else:
        return obj

def obj_hash(obj):
    return Hash(str(obj_canonical(obj))).compute()
