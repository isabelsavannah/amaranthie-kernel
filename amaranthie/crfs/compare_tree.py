import json
from amaranthie.crfs.hash import obj_hash, Hash
from amaranthie.crfs.types import Batch

class CompareTree:
    def __init__(self):
        self.root = CompareBranch()

    def insert(self, fact):
        path = Hash(fact["key"]).compute().hex()
        self.root.insert(path, fact)

    def explore(self, batch, side_effects):
        for prompt in batch["prompts"]:
            path = prompt["path"]
            yield from self.root.challenge(path, prompt, side_effects)

    def run_queries(self, batch):
        for path in batch["queries"]:
            yield from self.root.query(path)

    def handle_batch(self, batch):
        result = ComparePromptResultData(incoming_query_results)
        result.explore_iter = explore(batch, result)
        return result

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
            print(self.hash)
        elif not self.value:
            # We're an empty node, adopt this value
            self.value = fact
            self.hash = obj_hash(fact)
        elif fact["key"] == self.value["key"]:
            # An overwriting insert
            self.value = fact
            self.hash = Hash(json.dumps(fact)).compute()
        else:
            # We were a leaf, need to split
            self.children = {}
            self.insert(path, self.value)
            self.value = None
            self.insert(path, fact)

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
        elif self.children:
            for key in self.children:
                yield from self.children[key].query(path)
        elif self.value:
            yield from [self.value]
        else:
            yield from []

    def challenge(self, path, prompt, side_effects):
        # The prompt is the statement that our counterpart has a node with a
        # certain hash at a certain point. path is the progress towards that
        # point in our tree. 

        # Return an iterator of prompts to return to them in a challenge, while
        # issuing download requests and shares through the side effects object.

        if len(path) > 0:
            # The challenge refers to some point inside our subtree. Does that
            # geography exist for us?
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
                    yield from [Prompt(path+branch, self.children[branch].hash) for branch in shuffled(self.children.keys())]
                elif self.value:
                    # They may have a different value or a whole tree, either way exchange:
                    side_effects.query(prompt["path"])
                    side_effects.send(self.value)
                    yield from []
                else:
                    # They have data and we don't:
                    side_effects.query(prompt["path"])
                    yield from []

class ComparePromptResultData:
    # collect the iterators and such

    def __init__(self, incoming_queries):
        self.saved_query_paths = []
        self.saved_accept_paths = []
        self.saved_send_set = {}
        self.incoming_queries = incoming_queries
        self.queries_cap = config.get(config.crfs_queries_per_message)

    def assemble_response_batch(self):
        new_prompts = list(itertools.islice(new_prompts, self.queries_cap))
        new_queries = list(itertools.islice(self.saved_query_paths, self.queries_cap))

        return Batch(new_prompts, new_queries)

    def unique_facts(self, facts):
        so_far = {}
        for fact in facts:
            key = fact["key"]
            if key in so_far:
                continue
            else:
                so_far[key] = True
                yield fact

    def facts_to_send(self):
        return itertools.islice(unique_facts(zip(self.incoming_queries, self.saved_send_set.values())), self.queries_cap)

    def has_accepted(path):
        for accept_path in self.saved_accept_paths:
            if path == acceptPath or path.startswith(acceptPath):
                return True
        return False

    def send(self, value):
        self.send_set[value["key"]] = value

    def query(self, path):
        self.combine(self.query_paths, path)

    def accept(self, path):
        self.combine(self.accept_paths, path)

    def combine(self, current, new):
        for current_i in current:
            if new.startswith(current_i):
                return
            elif current_i.startswith(new):
                current.remove(current_i)
                combine(current, new)
                return
        current.append(new)

