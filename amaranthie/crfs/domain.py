from amaranthie import local_pubsub
from amaranthie.activity import Activity

class Domain(Activity):
    known = {}

    def __init__(self, name):
        super().__init__(name + " domain")
        self.name = name
        self.prefix = ['crfs', name]
        self.facts_topic = ['crfs', name, 'fact']
        self.batches_topic = ['crfs', name, 'batch']

    async def handle_batch(self, batch):
        pass

    async def handle_fact(self, fact):
        pass

    async def start(self):
        local_pubsub.sub(self.facts_topic, self.handle_fact)
        local_pubsub.sub(self.batches_topic, self.handle_batch)

    @staticmethod
    def define(name):
        if name in Domain.known:
            raise ValueError("domain " + name + " already exists")
        else:
            Domain.known[name] = Domain(name)
    
    @staticmethod
    def get(name):
        if name not in Domain.known:
            Domain.define(name)
        return Domain.known[name]
