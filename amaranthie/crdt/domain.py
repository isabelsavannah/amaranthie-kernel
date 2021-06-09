from amaranthie import directory
from amaranthie import local_pubsub

swarm = Domain("swarm")

class Domain:
    # one thread of the logic for keeping crdts sync'd, as a potential aggregation point

    def __init__(self, name):
        self.name = name
        self.prefix = [name]
        self.channel_base = "crdt_protocol"

    def get(self, name, typename):
        return directory.obtain_crdt_instance(name, typename, self.prefix)

    def listen_updates(self):
        channel = self.channel_base + "_instant"
        local_pubsub.sub(channel, self._handle_update)

    async def _handle_update(self, message):
        #TODO
        #see, now we're really wanting a unified dotted-path kinda type, aren't we?


    def share(self, full_id, update_string):
        #TODO
        pass

    def recv(self):
        #TODO: also this
        pass
