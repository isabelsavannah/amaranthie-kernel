from amaranthie import config
from amaranthie.crfs import timestamp

def Fact(key, value, update_time=None, author=None):
    if not update_time:
        update_time = timestamp.now()
    if not author:
        author = config.get(config.my_id)
    return {"key": key,
            "value": value,
            "update_time": timestamp.now(),
            "author": config.get(config.my_id)}

def Prompt(path, hash_bytes):
    return {"path": path, "hash": hash_bytes.encode()}

def Batch(prompts, queries):
    return {"prompts": prompts, "queries": queries}
