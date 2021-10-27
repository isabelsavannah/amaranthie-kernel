from amaranthie import local_pubsub
from amaranthie import net
from amaranthie.activity import Activity
from amaranthie.crfs.crfs_view import CrfsView
from amaranthie.crfs.compare_tree import CompareTree
from amaranthie.crfs.types import Batch, Prompt

import logging

class Domain(Activity):
    known = {}

    def __init__(self, name):
        super().__init__(name + " domain")
        self.name = name
        self.prefix = ['crfs', name]
        self.facts_topic = ['crfs', name, 'fact']
        self.batches_topic = ['crfs', name, 'batch']

        self.view = CrfsView(name, domain_ref = self)
        self.tree = CompareTree()

        self.log = logging.getLogger("amaranthie.domain." + name)

    async def handle_batch(self, msg):
        batch = msg["data"]
        sender = msg["sender"]

        self.log.info("Handling a crfs query batch from %s with %d prompts, %d queries", 
                str(sender),
                len(batch["prompts"]), 
                len(batch["queries"]))

        result = self.tree.handle_batch(batch)

        response = result.assemble_response_batch()
        facts = result.facts_to_send()

        self.log.info("Produced a crfs query response batch for %s with %d prompts, %d queries", 
                str(sender),
                len(response["prompts"]),
                len(response["queries"]))

        if response["queries"] or response["prompts"]:
            await net.lazy_send(sender, self.batches_topic, response)

        for fact in facts:
            self.log.debug("sending %s to %s", fact["key"], str(sender))
            await net.lazy_send(sender, self.facts_topic, response)

    def update(self, fact):
        self.log.debug("applying an update to %s to local hash tree", fact["key"])
        self.tree.insert(fact)

    def share(self, fact):
        self.log.debug("broadcasting an update to %s to", fact["key"])
        net.lazy_broadcast(self.facts_topic, fact)

    def noop(self, fact):
        pass

    def root_query(self):
        return Batch([
            Prompt("", self.tree.root.hash)],
            [])

    async def handle_fact(self, msg):
        fact = msg["data"]
        self.log.debug("recieved a fact %s", fact["key"])
        self.view.offer(fact)

    async def start(self):
        local_pubsub.sub(self.facts_topic, self.handle_fact)
        local_pubsub.sub(self.batches_topic, self.handle_batch)

    async def run(self):
        self.log.warning("SUPER fucking hacky")
        import sys
        import random
        from amaranthie.random_util import random_id
        if(int(sys.argv[1]) == 0):
            self.log.info("initiating prototype sync")
            view = CrfsView(self.name)
            swip = self.share
            self.share = self.noop
            path = []
            for i in range(100):
                if random.randint(0, 9) <= 2:
                    path = path + [random_id()[0:4]]
                if random.randint(0, 9) <= 2 and path:
                    path = path[:-1]
                self.view[path + [random_id()]] = random_id()
            self.share = swip
            self.log.info("loaded test data")

            await net.lazy_send(net.get_random_peer_ref(), self.batches_topic, self.root_query())

    @staticmethod
    def define(name):
        if name in Domain.known:
            raise ValueError("domain " + name + " already exists")
        else:
            Domain.known[name] = Domain(name)
    
    @staticmethod
    def get(name, create=True):
        if name not in Domain.known and create:
            Domain.define(name)
        return Domain.known[name]
