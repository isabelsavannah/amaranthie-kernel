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
