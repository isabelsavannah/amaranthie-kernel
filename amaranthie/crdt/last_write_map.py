from amaranthie import fsdb
from amaranthie.crdt import timestamp
import json 

class LastWriteMap:

    def __init__(self, prefix, server):
        # if something is in memory, guarentee that it is the most updated version
        self._mem_collection = {}
        self._fsview = fsdb.FsView(prefix)
        self._server = server
        super().__init__()

    def __getitem__(self, key):
        if key not in self._mem_collection && key in self._fsview:
            self._load_mem(key)
        return self._mem_collection[key].value

    def __setitem__(self, key, value):
        update = LastWriteMapUpdate(key, value)
        if self._apply_mem(update):
            self._server.share(self.prefix, update)
            self._persist_mem(key)

    def recv(self, update_str):
        update = LastWriteMapUpdate.from_string(update_str)
        if self._apply_mem(update):
            self._persist_mem(update.key)

    def _apply_mem(self, update):
        # return: did this update actually supplant our copy?
        key = update.key
        if key in self._mem_collection:
            return self._mem_collection[key].apply(update)
        else if key in self._fsview:
            self._load_mem(key)
            return self._mem_collection[key].apply(update)
        else:
            self._mem_collection[key] = LastWriteMapValue.fromUpdate(update)
            return true

    def _persist_mem(self, key):
        self._fsview[key] = str(self._mem_collection[key])

    def _load_mem(self, key):
        self._mem_collection[key] = LastWriteMapValue.fromString(self._fsview[key])

def replace_with_now(update_time):
    return update_time if update_time else timestamp.now()

class LastWriteMapValue:
    def __init__(self, value, update_time = None):
        self.value = value
        self.update_time = replace_with_now(update_time)

    def __str__(self):
        return json.dumps({"value": self.value, "timestamp": self.update_time})

    @classMethod
    def from_string(cls, json_str):
        obj = json.loads(json_str)
        return cls(obj["value"], obj["timestamp"])

    @classMethod
    def from_update(cls, update):
        return cls(update.value, update.update_time)

    def apply(self, update):
        if update.update_time > self.update_time:
            self.value = update.value
            self.update_time = update_time
            return True
        else:
            return False

class LastWriteMapUpdate:
    def __init__(self, key, value, update_time = None):
        self.value = value
        self.key = key
        self.update_time = replace_with_now(update_time)

    def __str__(self):
        return json.dumps({"key": self.key, "value": self.value, "timestamp": self.update_time})

    @classMethod
    def from_string(cls, json_str):
        obj = json.loads(json_str)
        return cls(obj["key"], obj["value"], obj["timestamp"])
