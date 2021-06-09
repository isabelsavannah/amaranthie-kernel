from amaranthie import fsdb
from threading import Lock

registered = {}
live = {}

singleton_server = "woop woop woop!"

def register_crdt(typename, construct):
    registered[typename] = construct

def encode(name, typename):
    return "-".join([typename, name])

def decode(key):
    return key.split("-")

def obtain_crdt_instance(name, typename, prefix):
    canonical_name = fsdb.flatten_id(prefix, encode(isntance_id, name))

    if canonical_name not in live:
        live[canonical_name] = _construct(name, typename, prefix)

    return live[canonical_name]

def _construct(typename, path):
    return registered[typename](path, singleton_server)





