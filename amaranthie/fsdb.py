from amaranthie.config import config
import os
import shutil

state_root = config["state"]["path"]
encoding = config["state"]["encoding"]

def get_keys(prefix):
    try:
        return os.listdir(_pathify(prefix))
    except FileNotFoundError as err:
        return []

def get(prefix, key):
    with open(_pathify(prefix, key), mode='rt', encoding=encoding) as f:
        return f.read()

def put(prefix, key, value):
    os.makedirs(_pathify(prefix), exist_ok=True)
    with open(_pathify(prefix, key), mode='wt', encoding=encoding) as f:
        f.write(value)

def delete(prefix, key):
    os.remove(_pathify(prefix, key))

def delete_set(prefix):
    shutil.rmtree(_pathify(prefix))

def _pathify(*args):
    dirs = list(_pathify_generator(args))
    full = os.path.relpath(os.path.join(state_root, *dirs))
    return full

def _pathify_generator(args):
    for element in args:
        if isinstance(element, str):
            yield element
        else:
            yield from _pathify_generator(element)

