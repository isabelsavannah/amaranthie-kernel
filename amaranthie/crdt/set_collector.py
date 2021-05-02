from abc import ABC
from abc import abstractmethod

class SetCollector(ABC):
    # common functionality for CRDTs where we can represent both updates and
    # persistent state as a set of discrete elements

    def __init__(self):
        self.collection = {}

    @abstractmethod
    def crdt_name(self):
        pass

    @abstractmethod
    def consider(self, update):
        pass

    def keep(self, key, value):
        pass

class Register(SetCollector):

    def consider(self, update):
        if len(self.collection) == 0:
            keep("value", update)
        else:
            if self.collection["value"]["timestamp"] < update["timestamp"]:
                keep("value", update)

    def crdt_name(self):
        return "register"

class LastWriteMap(SetCollector):

    def consider(self, update):
        key = update["key"]
        if key in self.collection.keys():
            current = self.collection[key]
            if update["timestamp"] > current["timestamp"]:
                keep(key, update)

    def crdt_name(self):
        return "last_write_map"


