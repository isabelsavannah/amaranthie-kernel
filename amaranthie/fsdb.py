from amaranthie.config import config
import os
import shutil

state_root = config["state"]["path"]
encoding = config["state"]["encoding"]

def get_keys(prefix):
    try:
        return os.listdir(pathify(prefix))
    except FileNotFoundError as err:
        return []

def has(prefix, key):
    return os.path.exists(pathify(prefix, key))

def get(prefix, key):
    with open(pathify(prefix, key), mode='rt', encoding=encoding) as f:
        return f.read()

def put(prefix, key, value):
    os.makedirs(pathify(prefix), exist_ok=True)
    with open(pathify(prefix, key), mode='wt', encoding=encoding) as f:
        f.write(value)

def delete(prefix, key):
    os.remove(pathify(prefix, key))

def delete_set(prefix):
    shutil.rmtree(pathify(prefix))

def pathify(*args):
    dirs = flatten_id
    full = os.path.relpath(os.path.join(state_root, *dirs))
    return full

class FsView:
    def __init__(self, prefix, parent = None):
        self.prefix = flatten_id([parent.prefix, prefix] if parent else prefix)

    def __contains__(self, key):
        return has(self.prefix, key)

    def __getitem__(self, key):
        return get(self.prefix, key)

    def __setitem(self, key):
        return put(self.prefix, key)

