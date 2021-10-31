from amaranthie import local_pubsub
from amaranthie import net
from amaranthie.activity import Activity
from amaranthie.crfs.crfs_view import CrfsView
from amaranthie.crfs.compare_tree import CompareTree
from amaranthie.crfs.types import Batch, Prompt
from amaranthie.random_util import random_delay

import logging
import asyncio

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
        self.log.warning("hacky...")
        sender = msg["lazy_sender"]

        self.log.info("Handling a crfs query batch from %s with %d prompts, %d queries", 
                str(sender),
                len(batch["prompts"]), 
                len(batch["queries"]))
        try:
            self.log.debug("prompts at %s", [prompt["path"] for prompt in batch["prompts"]])
        except Exception as ex:
            print(batch)
            raise ex
        self.log.debug("queries at %s", batch["queries"])

        result = self.tree.handle_batch(batch)

        response = result.assemble_response_batch()
        facts = result.facts_to_send()

        self.log.info("Produced a crfs query response batch for %s with %d prompts, %d queries", 
                str(sender),
                len(response["prompts"]),
                len(response["queries"]))

        self.log.info("delaying result")
        await asyncio.sleep(10)

        facts_count = 0
        for fact in facts:
            self.log.debug("sending %s to %s", fact["key"], str(sender))
            await net.lazy_send(sender, self.facts_topic, fact)
            facts_count += 1
        self.log.info("sent %d facts to %s", facts_count, str(sender))

        if not response["prompts"] and '' not in result.accept_paths:
            self.log.info("Adding a root prompt to the response because we do not appear to be done")
            response["prompts"].append(self.root_prompt())

        if response["queries"] or response["prompts"]:
            await net.lazy_send(sender, self.batches_topic, response)
        else:
            self.log.debug("Not sending response batch because it is empty")
            self.log.debug("my root hash is now %s", self.tree.root.hash.hex())
            self.tree.root.debug_print()
            self.log.debug("buffer clear?")

    def update(self, fact):
        self.log.debug("applying an update to %s to local hash tree", fact["key"])
        self.tree.insert(fact)

    def share(self, fact):
        self.log.debug("broadcasting an update to %s to", fact["key"])
        net.lazy_broadcast(self.facts_topic, fact)

    def root_prompt(self):
        return Prompt("", hash_bytes=self.tree.root.hash)

    def root_batch(self):
        return Batch([self.root_prompt()],
            [])

    async def handle_fact(self, msg):
        fact = msg["data"]
        self.log.debug("recieved a fact %s", fact["key"])
        self.view.offer(fact)

    async def start(self):
        local_pubsub.sub(self.facts_topic, self.handle_fact)
        local_pubsub.sub(self.batches_topic, self.handle_batch)

    def noop(self, fact):
        pass

    async def run(self):
        self.log.warning("SUPER fucking hacky")
        import sys
        import random
        from amaranthie.random_util import random_id

        self.log.info("initiating prototype sync")
        view = CrfsView(self.name)
        swip = self.share
        self.share = self.noop
        path = []
        for i in range(1000):
            if random.randint(0, 9) <= 2:
                path = path + [random_id()[0:4]]
            if random.randint(0, 9) <= 2 and path:
                path = path[:-1]
            self.view[path + [random_id()]] = random_id()
        self.share = swip
        self.log.info("loaded test data")
        self.tree.root.debug_print()

        await asyncio.sleep(random_delay(30))
        peer = net.get_random_peer_ref()
        self.log.debug("starting test sync with %s", peer)
        await net.lazy_send(peer, self.batches_topic, self.root_batch())

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
