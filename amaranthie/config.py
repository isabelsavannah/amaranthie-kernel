from amaranthie.random_util import random_id
from amaranthie import logging_util
from amaranthie.rich_id import RichId

my_id = "id"

peers_listen_port = "peers/listen_port"
peers_heartbeat_interval_seconds = "peers/heartbeat_interval_seconds"
peers_connect_interval_seconds = "peers/connect_interval_seconds"

state_path = "state/path"
state_encoding = "state/encoding"

crfs_queries_per_message = "4"

hardcoded_default = {
  "id": random_id(),

  "peers": {
    "listen_port": 2000,
    "heartbeat_interval_seconds": 300,
    "connect_interval_seconds": 30,
  },

  "state": {
    "path": "state",
    "encoding": "utf-8",
  },
}

def get(key):
    sources = [hardcoded_default]

    for token in RichId(key):
        sources = [source[token] for source in sources if token in source]
        if len(sources) == 0:
            return None

    return sources[0]
