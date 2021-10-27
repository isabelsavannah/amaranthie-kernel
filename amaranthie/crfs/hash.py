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
    if isinstance(obj, collections.Mapping):
        return [[k, obj_canonical(k)] for k in sorted(obj.keys())]
    if isinstance(obj, collections.Sequence):
        return [i for i in obj]
    return obj

def obj_hash(obj):
    return Hash(str(obj_canonical(obj))).compute()
