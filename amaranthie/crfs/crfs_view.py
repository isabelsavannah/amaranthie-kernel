import json
from amaranthie.crfs import timestamp
from amaranthie.crfs.types import Fact
from amaranthie.fsdb import FsView
from amaranthie import config

import logging
log = logging.getLogger(__name__)

class CrfsView:
    def __init__(self, domain, prefix = [], domain_ref = None):
        if domain_ref:
            self.domain = domain_ref
        else:
            from amaranthie.crfs.domain import Domain
            self.domain = Domain.get(domain, False)
            assert(self.domain)
        self.fs = FsView(['crfs', domain, prefix])

    def __contains__(self, key):
        return key in self.fs

    def __getitem__(self, key):
        # might want to cache 
        return json.loads(self.fs[key])["value"]

    def set_fact(self, fact):
        key = fact["key"]
        if key in self:
            old_fact = self[key]
            if fact["timestamp"] <= old_fact["timestamp"]:
                return False
        self.fs[key] = json.dumps(fact)
        return True

    def __setitem__(self, key, value):
        fact = Fact(key, value)
        if self.set_fact(fact):
            self.domain.share(fact)
            self.domain.update(fact)

    def offer(self, fact):
        if self.set_fact(fact):
            self.domain.update(fact)

    def __iter__(self, key):
        return self.fs.__iter__(key)
