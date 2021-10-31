from amaranthie import config
from amaranthie.crfs import timestamp
from amaranthie.rich_id import RichId

def Fact(key, value, update_time=None, author=None):
    key = str(RichId(key))
    if len(key) < 5:
        raise "here"
    if not update_time:
        update_time = timestamp.now()
    if not author:
        author = config.get(config.my_id)
    return {"key": key,
            "value": value,
            "update_time": timestamp.now(),
            "author": config.get(config.my_id)}

def Prompt(path, hash_bytes = None, hash_string = None):
    if hash_bytes != None:
        return {"path": path, "hash": hash_bytes.hex()}
    elif hash_string != None:
        return {"path": path, "hash": hash_string}
    else:
        raise ValueError("require hash_bytes or hash_string")


def Batch(prompts, queries):
    return {"prompts": prompts, "queries": queries}
