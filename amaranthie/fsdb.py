from amaranthie import config
from amaranthie.rich_id import RichId
import os
import shutil

state_root = config.get(config.state_path)
encoding = config.get(config.state_encoding)

def get_keys(prefix):
    try:
        return os.listdir(pathify(prefix))
    except FileNotFoundError as err:
        return []

def has(prefix, key):
    return os.path.exists(pathify(prefix, key))

def get(prefix, key):
    import pdb
    pdb.set_trace()
    with open(pathify(prefix, key), mode='rt', encoding=encoding) as f:
        return f.read()

def put(prefix, key, value):
    parent = RichId(prefix, key).id_words[:-1]
    os.makedirs(pathify(parent), exist_ok=True)
    with open(pathify(prefix, key), mode='wt', encoding=encoding) as f:
        f.write(value)

def delete(prefix, key):
    os.remove(pathify(prefix, key))

def delete_set(prefix):
    shutil.rmtree(pathify(prefix))

def pathify(*args):
    dirs = RichId(args).id_words
    full = os.path.relpath(os.path.join(state_root, *dirs))
    return full

class FsView:
    def __init__(self, prefix, parent = None):
        self.prefix = RichId([parent.prefix, prefix] if parent else prefix)

    def __contains__(self, key):
        return has(self.prefix, key)

    def __getitem__(self, key):
        return get(self.prefix, key)

    def __setitem__(self, key, value):
        return put(self.prefix, key, value)

    def __iter__(self, key):
        return get_keys(self.prefix, key).__iter__()

