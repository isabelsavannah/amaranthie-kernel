class LastWriteMap(SetCollector):

    def consider(self, update):
        key = update["key"]
        if key in self.collection.keys():
            current = self.collection[key]
            if update["timestamp"] > current["timestamp"]:
                keep(key, update)

    def crdt_name(self):
        return "last_write_map"



