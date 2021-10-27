from amaranthie.crdt import timestamp
from amaranthie import config
from amaranthie import config
from dataclasses import dataclass
import hashlib
import itertools
import random

def Fact(key, value):
    return Fact(key, value, timestamp.now(), config.get(config.my_id))

def Fact(key, value, update_time, author):
    return {"key": key,
            "value": value,
            "update_time": timestamp.now(),
            "author": config.get(my_id)}

def Prompt(path, hash_bytes):
    return {"path": path, "hash": hash_bytes.encode()}

def Batch(prompts, queries):
    return {"prompts": prompts, "queries": queries}

class CrfsView:
    def __init__(self, domain, prefix = []):
        self.domain = domains[domain]
        assert(self.domain)
        self.fs = FsView(['crfs', domain, prefix])

    def __contains__(self, key):
        return key in self.fs

    def __getitem__(self, key):
        # might want to cache 
        return json.loads(self.fs[key])["value"]

    def __setitem__(self, key, value):
        fact = Fact.author(key, value)
        old_fact = self[key]
        if fact["timestamp"] > old_fact["timestamp"]:
            self.fs[key] = json.dumps(fact)
            self.domain.share(fact)

    def __iter__(self, key):
        return self.fs.__iter__(key)

class Domain:
    def __init__(self, name):
        self.name = name
        self.raw_view = FsView(['crfs', name])
        self.tree = CompareTree()

    def share(self, new_fact):
        self.tree.insert(new_fact)
        pass
        # TODO: net here



class Hash:
    def __init__(self, data = None):
        self.crypt = hashlib.sha256
        self.encoding = 'utf-8'
        if data:
            self.write(data)

    def write(self, data):
        self.crypt.update(data.encode('utf-8'))

    def compute(self):
        return self.crypt.digest()

class CompareTree:
    class SideEffectsCollector:
        def __init__(self):
            self.query_paths = []
            self.accept_paths = []
            self.send_set = {}

        def send(self, value):
            self.send_set[value["key"]] = value

        def query(self, path):
            SideEffectsCollector.combine(self.query_paths, path)

        def accept(self, path):
            SideEffectsCollector.combine(self.accept_paths, path)

        @staticmethod
        def combine(current, new):
            for current_i in current:
                if new.startswith(current_i):
                    return
                else if current_i.startswith(new):
                    current.remove(current_i)
                    combine(current, new)
                    return
            current.append(new)

    def __init__(self):
        self.root = CompareBranch()

    def insert(self, fact):
        path = Hash(fact["key"]).compute().hex()
        self.root.insert(path, fact)

    def handle_batch(self, batch, net):
        side_effects = SideEffectsCollector()
        new_prompts = self.run_prompts(batch["prompts"], side_effects)

        queries_cap = config.get(config.crfs_queries_per_message)

        response_prompts = list(itertools.islice(new_prompts, queries_cap))
        random.shuffle(response_prompts)

        for key in itertools.islice(side_effects.send_set().keys()):
            net.send_fact(side_effects.send_set[key])

        response = Batch(response_prompts, side_effects.query_paths)

        if "" not in side_effects.accept_paths && len(response["prompts"]) == 0:
            response["prompts"] = [Prompt("", self.root.hash)]

        if len(response["prompts"]) == 0 && len(response["queries"]) == 0:
            return None

        return response

    def run_prompts(self, prompts, side_effects):
        for prompt in prompts:
            path = prompt["path"]
            yield from self.root.challenge(path, prompt, side_effects)

class CompareBranch:
    def __init__(self):
        self.children = None
        self.value = None
        self.hash = ""

    def insert(self, path, fact):
        if self.children:
            # We have children, so we pass to appropriate child and rehash
            branch = path[0]
            if branch not in self.children:
                self.children[branch]=CompareBranch()
            self.children[branch].insert(path[1:], fact)

            hash_progress = Hash()
            for branch in self.children:
                hash_progress.write(self.children[branch].hash)

            self.hash = hash_progress.compute()
            return
        else if not self.value:
            # We're an empty node, adopt this value
            self.value = fact
            self.hash = Hash(json.dumps(fact)).compute()
        else if fact["key"] == self.value["key"]:
            # An overwriting insert
            self.value = fact
            self.hash = Hash(json.dumps(fact)).compute()
        else:
            # We were a leaf, need to split
            self.children = {}
            self.insert(value)
            self.value = None
            self.insert(fact)

    def query(self, path):
        # Return an iterator of stored facts that could be provided in response
        # to this query path
        if len(path) > 0:
            branch = path[0]
            if branch in self.children:
                rest = path[1:]
                return self.children[branch].query(rest)
            else:
                yield from []
        else if self.value:
            yield from [self.value]
        else if self.children:
            for key in self.children:
                yield from self.children[key].query("")
        else:
            yield from []

    def challenge(self, path, prompt, side_effects):
        # The prompt is the statement that our counterpart has a node with a
        # certain hash at a certain point. path is the progress towards that
        # point in our tree. 

        # Return an iterator of prompts to return to them in a challenge, while
        # issuing download and shares through the side effects object.

        if len(path) > 0:
            # The challenge refers to some point inside our subtree. Does that
            # grography exist for us?
            branch = path[0]
            rest = path[1:]
            if branch in self.children:
                return self.children[branch].challenge(rest, prompt, side_effects)
            else:
                side_effects.query(prompt["path"])
                yield from []
        else:
            # The challenge refers to our location exactly. Do we match it?
            if prompt["hash"] == self.hash:
                # No disagreement, so no further investigation is required
                side_effects.accept(prompt["path"])
                yield from []
            else:
                # They have a different value here than us. They may or may not
                # be the same kind as us, but they can't be fully identical
                if self.children:
                    # If they don't have children, we share, if they do, we recurse. Either way:
                    yield from [Prompt(path+branch, self.children[branch].hash) for branch in self.children.keys()]
                else if self.value:
                    # They may have a different value or a whole tree, either way exchange:
                    side_effects.query(prompt["path"])
                    side_effects.send(self.value)
                    yield from []
                else:
                    # They have data and we don't:
                    side_effects.query(prompt["path"])
                    yield from []
