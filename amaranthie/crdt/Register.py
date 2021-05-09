
class Register(SetCollector):

    def consider(self, update):
        if len(self.collection) == 0:
            keep("value", update)
        else:
            if self.collection["value"]["timestamp"] < update["timestamp"]:
                keep("value", update)

    def crdt_name(self):
        return "register"

