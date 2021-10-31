import json
import itertools
import logging
from amaranthie import config
from amaranthie.crfs.hash import obj_hash, Hash
from amaranthie.crfs.types import Batch, Prompt
from amaranthie.random_util import shuffled

log = logging.getLogger(__name__)

hex_bytes = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'a', 'b', 'c', 'd', 'e', 'f']

def path_for(fact):
    return Hash(fact["key"]).compute().hex()

class CompareTree:
    def __init__(self):
        self.root = CompareBranch('')

    def insert(self, fact):
        path = Hash(fact["key"]).compute().hex()
        log.debug("insert path is %s", path)
        self.root.insert(path, fact)

    def explore(self, batch, side_effects):
        for prompt in batch["prompts"]:
            path = prompt["path"]
            yield from self.root.challenge(path, prompt, side_effects)

    def run_queries(self, queries):
        for path in queries:
            log.debug("querying %s", path)
            yield from self.root.query(path)

    def handle_batch(self, batch):
        result = ComparePromptResultData(self.run_queries(batch["queries"]))
        result.explore_iter = self.explore(batch, result)
        return result

class CompareBranch:
    def __init__(self, path):
        self.children = None
        self.value = None
        self.hash = b''
        self.path = path

    def debug_print(self, indent=0):
        if self.children: 
            print(' '*indent, self.path, self.hash.hex())
            for child in self.children.values():
                child.debug_print(indent+1)
        else:
            print(' '*indent, path_for(self.value)[0:8], self.hash.hex(), self.value["key"])

    def insert(self, path, fact):
        if self.children != None:
            # We have children, so we pass to appropriate child and rehash
            branch = path[0]
            log.debug("%s: inserting %s in %s child", self.path, fact["key"], branch)
            if branch not in self.children:
                log.debug("creating new child")
                self.children[branch]=CompareBranch(self.path + branch)
            self.children[branch].insert(path[1:], fact)

            hash_progress = Hash()
            for branch in sorted(self.children.keys()):
                hash_progress.write(self.children[branch].hash)

            self.hash = hash_progress.compute()
        elif not self.value:
            log.debug("%s: inserting %s here", self.path, fact["key"])
            # We're an empty node, adopt this value
            self.value = fact
            self.hash = obj_hash(fact)
        elif fact["key"] == self.value["key"]:
            log.debug("%s: replacing %s here", self.path, fact["key"])
            # An overwriting insert
            self.value = fact
            self.hash = Hash(json.dumps(fact)).compute()
        else:
            # We were a leaf, need to split
            self.children = {}

            log.debug("splitting node at %s to insert %s, currently %s", self.path, path_for(fact), path)

            prev_path = path_for(self.value)
            log.debug("restored facts node's path as %s", prev_path)
            masked_prev_path = prev_path[len(self.path):]
            log.debug("masked to %s", masked_prev_path)
            log.debug("reinserting old node")
            self.insert(masked_prev_path, self.value)
            self.value = None

            log.debug("reinserting new fact")
            self.insert(path, fact)

    def query(self, path):
        # Return an iterator of stored facts that could be provided in response
        # to this query path
        log.debug("query at %s, rest %s", self.path, path)
        if len(path) > 0:
            branch = path[0]
            if branch in self.children:
                log.debug("recursing to find root of query")
                rest = path[1:]
                yield from self.children[branch].query(rest)
            else:
                log.debug("we have nothing under this tree; halting")
                yield from []
        elif self.children:
            log.debug("recursing to enumerate query results")
            for key in shuffled(self.children.keys()):
                yield from self.children[key].query(path)
        elif self.value:
            log.debug("returning my value: %s", self.value)
            yield self.value
        else:
            log.debug("returning NOTZING, lebowski")
            yield from []

    def challenge(self, path, prompt, side_effects):
        # The prompt is the statement that our counterpart has a node with a
        # certain hash at a certain point. path is the progress towards that
        # point in our tree. 

        # Return an iterator of prompts to return to them in a challenge, while
        # issuing download requests and shares through the side effects object.

        log.debug("challenge at %s with rest %s", self.path, path)
        if len(path) > 0:
            # The challenge refers to some point inside our subtree. Does that
            # geography exist for us?
            branch = path[0]
            rest = path[1:]
            if self.children and branch in self.children:
                log.debug("recursing to %s child", branch)
                yield from self.children[branch].challenge(rest, prompt, side_effects)
            elif not prompt["hash"]:
                log.debug("we agree with negative challenge")
                side_effects.accept(prompt["path"])
            else:
                log.debug("missing child %s, responding with a query", branch)
                side_effects.query(prompt["path"])
                yield from []
        else:
            # The challenge refers to our location exactly. Do we match it?
            if not prompt["hash"]:
                # They do not have this subtree, send our entire subtree
                log.debug("we disagree with negative challenge; sending our subtree")
                side_effects.send_all(self.query(''))
            elif prompt["hash"] == self.hash.hex():
                log.debug("we agree with this prompt")
                log.debug("my hash %s their hash %s", self.hash.hex(), prompt["hash"])
                log.debug("my value %s", self.value)
                side_effects.accept(prompt["path"])
                yield from []
            else:
                # They have a different value here than us. They may or may not
                # be the same kind as us, but they can't be fully identical
                if self.children:
                    # If they don't have children, we share, if they do, we recurse. Either way:
                    log.debug("we disagree with this query here; returning a prompt for each of our children")
                    for branch in shuffled(hex_bytes):
                        next_path = self.path+branch
                        if branch in self.children:
                            yield Prompt(next_path, self.children[branch].hash)
                        else:
                            yield Prompt(next_path, hash_string = '')
                elif self.value:
                    # They may have a different value or a whole tree, either way exchange:
                    log.debug("we disagree with this query here and we are a leaf; returning our value and a query here")
                    side_effects.query(prompt["path"])
                    side_effects.send(self.value)
                    yield from []
                else:
                    # They have data and we don't:
                    log.debug("prompt is here but we're an empty leaf; returning a query here")
                    side_effects.query(prompt["path"])
                    yield from []

class ComparePromptResultData:
    # collect the iterators and such

    def __init__(self, incoming_queries_results):
        self.query_paths = []
        self.accept_paths = []
        self.send_facts_bare = []
        self.send_facts_iters = []
        self.incoming_queries_results = incoming_queries_results
        self.queries_cap = config.get(config.crfs_queries_per_message)

    def assemble_response_batch(self):
        new_prompts = list(itertools.islice(self.explore_iter, self.queries_cap))
        new_queries = list(itertools.islice(self.query_paths, self.queries_cap))

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

    def merge_iterators(self, iters_list):
        for tup in itertools.zip_longest(*shuffled(iters_list)):
            for item in tup:
                if item:
                    yield item

    def facts_to_send(self):
        facts = self.merge_iterators([self.incoming_queries_results, self.send_facts_bare] 
                + self.send_facts_iters)
        return itertools.islice(self.unique_facts(facts), self.queries_cap)

    def has_accepted(path):
        for accept_path in self.accept_paths:
            if path == acceptPath or path.startswith(acceptPath):
                return True
        return False

    def send(self, value):
        self.send_facts_bare.append(value)

    def send_all(self, value_iter):
        self.send_facts_iters.append(value_iter)

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

